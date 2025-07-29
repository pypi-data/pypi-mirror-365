/**
 * Mixin for use with calendar components.
 */

import { gqlCalendar } from "./calendar.graphql";

const calendarMixin = {
  props: {
    calendarFeeds: {
      type: Array,
      required: false,
      default: () => [],
    },
    params: {
      type: Object,
      required: false,
      default: null,
    },
  },
  data() {
    return {
      calendar: {
        calendarFeeds: [],
      },

      selectedEvent: null,

      fetchedDateRanges: [],
      fetchMoreInterval: null,

      title: "",

      range: {
        start: null,
        end: null,
      },
    };
  },
  emits: ["changeCalendarType", "changeCalendarFocus", "selectEvent"],
  apollo: {
    calendar: {
      query: gqlCalendar,
      skip: true,
    },
  },
  computed: {
    paramsForSend() {
      if (this.params !== null) {
        return JSON.stringify(this.params);
      }
      return null;
    },
    extendedStart() {
      let extendedStart;
      if (this.$refs.calendar) {
        extendedStart = this.$refs.calendar.getStartOfWeek(
          this.range.start,
        ).date;
      } else {
        extendedStart = this.range.start?.date;
      }
      return this.$parseISODate(extendedStart);
    },
    extendedEnd() {
      let extendedEnd;
      if (this.$refs.calendar) {
        extendedEnd = this.$refs.calendar.getEndOfWeek(this.range.end).date;
      } else {
        extendedEnd = this.range.end?.date;
      }
      return this.$parseISODate(extendedEnd).endOf("day");
    },
    queryVariables() {
      return {
        start: this.extendedStart.toISODate(),
        end: this.extendedEnd.toISODate(),
        names: this.calendarFeeds.map((f) => f.name),
        params: this.paramsForSend,
      };
    },
    mergedFetchedDateRanges() {
      let sortedRanges = this.fetchedDateRanges
        .slice()
        .sort((a, b) => a.start - b.start);

      let mergedRanges = [];

      for (const range of sortedRanges) {
        if (mergedRanges.length === 0) {
          mergedRanges.push(range);
        } else {
          let lastMergedRange = mergedRanges[mergedRanges.length - 1];
          let currentStartDate = range.start;
          let currentEndDate = range.end;
          let lastMergedEndDate = lastMergedRange.end.plus({ days: 1 });

          if (currentStartDate <= lastMergedEndDate) {
            lastMergedRange.end =
              currentEndDate > lastMergedEndDate
                ? currentEndDate
                : lastMergedRange.end;
          } else {
            mergedRanges.push(range);
          }
        }
      }

      return mergedRanges;
    },
  },
  watch: {
    params(newParams) {
      if (this.range.start && this.range.end) {
        this.refetchWithNewParams();
      }
    },
    calendarFeeds(newFeeds, oldFeeds) {
      if (
        !newFeeds
          .map((ncf) => ncf.name)
          .every((n) => oldFeeds.map((ocf) => ocf.name).includes(n))
      ) {
        this.refetchWithNewParams();
      }
    },
    range: {
      handler() {
        this.fetch();
      },
      deep: true,
      immediate: true,
    },
  },
  methods: {
    getColorForEvent(event) {
      if (event.status === "CANCELLED") {
        return event.color + "40";
      }
      return event.color;
    },
    getTextColorForEvent(event) {
      if (event.status === "CANCELLED") {
        return event.color;
      }
      return "white";
    },
    isFullyContained(start, end) {
      for (const existingRange of this.mergedFetchedDateRanges) {
        if (start >= existingRange.start && end <= existingRange.end) {
          return true;
        }
      }

      return false;
    },
    fetchMoreCalendarEvents(start, end) {
      this.$apollo.queries.calendar.fetchMore({
        variables: this.queryVariables,
        updateQuery: (previousResult, { fetchMoreResult }) => {
          let previousCalendarFeeds = previousResult.calendar.calendarFeeds;
          let newCalendarFeeds = fetchMoreResult.calendar.calendarFeeds;

          previousCalendarFeeds.forEach((calendarFeed, i, calendarFeeds) => {
            // Get all events except those that are updated
            let keepEvents = [];

            if (!start.invalid && !end.invalid) {
              keepEvents = calendarFeed.events.filter(
                (event) =>
                  !(
                    this.$parseISODate(event.end) <= end &&
                    this.$parseISODate(event.start) >= start
                  ),
              );
            } else if (!start.invalid) {
              keepEvents = calendarFeed.events.filter(
                (event) => !(this.$parseISODate(event.start) >= start),
              );
            } else if (!end.invalid) {
              keepEvents = calendarFeed.events.filter(
                (event) => !(this.$parseISODate(event.end) <= end),
              );
            }

            /// Update the events of the calendar feed
            calendarFeeds[i].events = [
              ...keepEvents,
              ...newCalendarFeeds[i].events,
            ];
          });
          return {
            calendar: {
              ...previousResult.calendar,
              calendarFeeds: previousCalendarFeeds,
            },
          };
        },
      });
    },
    refresh() {
      // Stop polling the query with old variables
      this.$apollo.queries.calendar.stopPolling();
      clearInterval(this.fetchMoreInterval);

      this.fetchMoreCalendarEvents(this.extendedStart, this.extendedEnd);

      this.fetchMoreInterval = setInterval(() => {
        this.fetchMoreCalendarEvents(this.extendedStart, this.extendedEnd);
      }, 30000);

      // Also reset the currently selected event (for the detail view)
      this.selectedEvent = null;
    },
    refetchWithNewParams() {
      // Stop polling the query with old variables
      this.$apollo.queries.calendar.stopPolling();
      clearInterval(this.fetchMoreInterval);

      this.$apollo.queries.calendar.setVariables(this.queryVariables);
      this.$apollo.queries.calendar.startPolling(30000);

      // Reset fetched date ranges to newly fetched date range
      this.fetchedDateRanges = [
        { start: this.extendedStart, end: this.extendedEnd },
      ];
    },
    fetch() {
      if (this.calendar.calendarFeeds.length === 0) {
        // No calendar feeds have been fetched yet,
        // so fetch all events in the current date range

        this.$apollo.queries.calendar.setVariables(this.queryVariables);
        this.$apollo.queries.calendar.skip = false;
        this.$apollo.queries.calendar.startPolling(30000);
        this.fetchedDateRanges.push({
          start: this.extendedStart,
          end: this.extendedEnd,
        });
      } else if (!this.isFullyContained(this.extendedStart, this.extendedEnd)) {
        this.refresh();

        this.fetchedDateRanges.push({
          start: this.extendedStart,
          end: this.extendedEnd,
        });
      } else {
        clearInterval(this.fetchMoreInterval);

        this.fetchMoreInterval = setInterval(() => {
          this.fetchMoreCalendarEvents(this.extendedStart, this.extendedEnd);
        }, 30000);

        // Also reset the currently selected event (for the detail view)
        this.selectedEvent = null;
      }
    },
  },
};

export default calendarMixin;
