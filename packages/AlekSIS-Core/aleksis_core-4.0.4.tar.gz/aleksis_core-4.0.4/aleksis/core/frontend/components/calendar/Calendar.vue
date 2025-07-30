<template>
  <div>
    <!-- Calendar title with current calendar time range -->
    <v-sheet :height="height">
      <v-expand-transition>
        <v-progress-linear
          v-if="$apollo.queries.calendar.loading"
          indeterminate
        />
      </v-expand-transition>
      <v-calendar
        ref="calendar"
        v-model="internalCalendarFocus"
        show-week
        :events="events"
        :weekdays="daysOfWeek"
        :type="internalCalendarType"
        :event-color="getColorForEvent"
        :event-text-color="getTextColorForEvent"
        :first-time="startWithFirstTime ? firstTime : undefined"
        interval-height="60"
        @click:date="viewDay"
        @click:day="viewDay"
        @click:more="viewDay"
        @click:event="viewEvent"
        @change="setCalendarRange"
      >
        <template #day-body="{ date, week }">
          <div
            class="v-current-time"
            :class="{ first: date === week[0].date }"
            :style="{ top: nowY }"
          ></div>
        </template>
        <template #event="{ event, eventParsed, timed }">
          <component
            :is="eventBarComponentForFeed(event.calendarFeedName)"
            :event="event"
            :event-parsed="eventParsed"
            :calendar-type="internalCalendarType"
          />
        </template>
        <template
          v-if="Object.keys(daysWithHiddenEvents).length"
          #interval-header
        >
          <div
            v-if="
              !internalCalendarType === 'day' ||
              Object.keys(daysWithHiddenEvents).includes(internalCalendarFocus)
            "
            class="d-flex justify-center align-end"
            :style="{ height: '100%' }"
          >
            <v-btn
              icon
              class="ma-2"
              @click="showAllAllDayEvents = !showAllAllDayEvents"
            >
              <v-icon>{{ showAllAllDayEventsButtonIcon }}</v-icon>
            </v-btn>
          </div>
        </template>
        <template #day-header="{ date }">
          <template
            v-if="
              Object.keys(daysWithHiddenEvents).includes(date) &&
              !showAllAllDayEvents
            "
          >
            <v-spacer />
            <div
              class="v-event-more ml-1"
              v-ripple
              @click="showAllAllDayEvents = true"
            >
              {{ $tc("calendar.more_events", daysWithHiddenEvents[date]) }}
            </div>
          </template>
        </template>
      </v-calendar>
      <component
        v-if="selectedEvent"
        :is="detailComponentForFeed(selectedEvent.calendarFeedName)"
        v-model="selectedOpen"
        :selected-element="selectedElement"
        :selected-event="selectedEvent"
        :calendar-type="internalCalendarType"
        @refreshCalendar="refresh()"
      />
    </v-sheet>
  </div>
</template>

<script>
import GenericCalendarFeedDetails from "./GenericCalendarFeedDetails.vue";
import GenericCalendarFeedEventBar from "./GenericCalendarFeedEventBar.vue";

import {
  calendarFeedDetailComponents,
  calendarFeedEventBarComponents,
} from "aleksisAppImporter";

import { gqlCalendar, calendarDaysPreference } from "./calendar.graphql";

import { Interval } from "luxon";

export default {
  name: "Calendar",
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
    // Start the calendar with the time of the first starting calendar event
    startWithFirstTime: {
      type: Boolean,
      required: false,
      default: () => false,
    },
    height: {
      type: String,
      required: false,
      default: "600",
    },
    calendarDaysOfWeek: {
      type: Array,
      required: false,
      default: undefined,
    },
    /**
     * What event/time to jump to.
     * Currently possible: `current` for current time, `first` for time of first visible event.
     * @values current, first
     */
    scrollTarget: {
      type: String,
      required: false,
      default: "current",
    },
    maxAllDayEvents: {
      type: Number,
      required: false,
      default: 5,
    },
  },
  data() {
    return {
      internalCalendarFocus: "",
      internalCalendarType: "week",

      calendar: {
        calendarFeeds: [],
      },

      selectedEvent: null,
      selectedElement: null,
      selectedOpen: false,

      fetchedDateRanges: [],
      fetchMoreInterval: null,

      title: "",

      range: {
        start: null,
        end: null,
      },

      firstTime: 1,
      scrolled: false,

      ready: false,

      personByIdOrMe: {
        id: null,
        preferences: {
          daysOfWeek: [1, 2, 3, 4, 5, 6, 0],
        },
      },

      showAllAllDayEvents: false,
      daysWithHiddenEvents: {},
    };
  },
  emits: ["changeCalendarType", "changeCalendarFocus", "selectEvent"],
  apollo: {
    calendar: {
      query: gqlCalendar,
      skip: true,
    },
    personByIdOrMe: {
      query: calendarDaysPreference,
      skip() {
        return this.calendarDaysOfWeek !== undefined;
      },
    },
  },
  computed: {
    rangeDateTime() {
      return {
        start: this.range.start
          ? this.$parseISODate(this.range.start.date)
          : null,
        end: this.range.end ? this.$parseISODate(this.range.end.date) : null,
      };
    },
    events() {
      let events = this.calendar.calendarFeeds
        .filter((c) => this.calendarFeeds.map((cf) => cf.name).includes(c.name))
        .flatMap((cf) =>
          cf.events.map((event) => {
            const start = this.$parseISODate(event.start);
            let end = this.$parseISODate(event.end);
            if (event.allDay) {
              end = end.minus({ days: 1 });
            }
            return {
              ...event,
              category: cf.verboseName,
              calendarFeedName: cf.name,
              start: start.toJSDate(),
              end: end.toJSDate(),
              startDateTime: start,
              endDateTime: end,
              color: event.color ? event.color : cf.color,
              timed: !event.allDay,
              meta: JSON.parse(event.meta),
            };
          }),
        );
      if (this.internalCalendarType === "month" || this.showAllAllDayEvents) {
        return events;
      }

      let dateFullEventCount = {};
      this.clearDaysWithHiddenEvents();

      return events.filter((event) => {
        if (!event.allDay) {
          return true;
        }
        const start = event.startDateTime;
        dateFullEventCount[start] = (dateFullEventCount[start] || 0) + 1;
        const show = dateFullEventCount[start] <= this.maxAllDayEvents;
        if (!show) {
          const dateInterval = Interval.fromDateTimes(
            start,
            event.endDateTime.endOf("day"),
          )
            .splitBy({ day: 1 })
            .map((date) => date.start.toISODate());
          for (const date of dateInterval) {
            this.daysWithHiddenEvents[date] =
              (this.daysWithHiddenEvents[date] || 0) + 1;
          }
        }
        return show;
      });
    },
    paramsForSend() {
      if (this.params !== null) {
        return JSON.stringify(this.params);
      }
      return null;
    },
    extendedStart() {
      let extendedStart = this.$refs.calendar.getStartOfWeek(
        this.range.start,
      ).date;
      return this.$parseISODate(extendedStart);
    },
    extendedEnd() {
      let extendedEnd = this.$refs.calendar.getEndOfWeek(this.range.end).date;
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
    cal() {
      return this.ready ? this.$refs.calendar : null;
    },
    nowY() {
      return this.cal ? this.cal.timeToY(this.cal.times.now) + "px" : "-10px";
    },
    daysOfWeek() {
      if (this.calendarDaysOfWeek !== undefined) {
        return this.calendarDaysOfWeek;
      }

      return this.personByIdOrMe.preferences.daysOfWeek;
    },
    showAllAllDayEventsButtonIcon() {
      return this.showAllAllDayEvents ? "mdi-chevron-up" : "mdi-chevron-down";
    },
  },
  watch: {
    params(newParams) {
      if (this.range.start && this.range.end) {
        this.refetchWithNewParams();
      }
    },
    calendarFeeds(newFeeds, oldFeeds) {
      this.updateMinTime();

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
        this.updateMinTime();
        this.fetch();
      },
      deep: true,
    },
    events: {
      handler() {
        this.updateMinTime();
      },
      deep: true,
    },
    internalCalendarType(val) {
      this.$emit("changeCalendarType", val);
    },
    internalCalendarFocus(val) {
      this.$emit("changeCalendarFocus", val);
    },
    selectedEvent(val) {
      this.$emit("selectEvent", val);
    },
  },
  methods: {
    prev() {
      this.$refs.calendar.prev();
    },
    next() {
      this.$refs.calendar.next();
    },
    setCalendarFocus(val) {
      this.internalCalendarFocus = val;
    },
    setCalendarType(val) {
      this.internalCalendarType = val;
    },
    viewDay({ date }) {
      this.internalCalendarFocus = date;
      this.internalCalendarType = "day";
    },
    viewEvent({ nativeEvent, event }) {
      const open = () => {
        this.selectedEvent = event;
        this.selectedElement = nativeEvent.target;
        requestAnimationFrame(() =>
          requestAnimationFrame(() => (this.selectedOpen = true)),
        );
      };

      if (this.selectedOpen) {
        this.selectedOpen = false;
        requestAnimationFrame(() => requestAnimationFrame(() => open()));
      } else {
        open();
      }

      nativeEvent.stopPropagation();
    },
    detailComponentForFeed(feedName) {
      if (
        this.calendar.calendarFeeds &&
        feedName &&
        Object.keys(calendarFeedDetailComponents).includes(feedName + "details")
      ) {
        return calendarFeedDetailComponents[feedName + "details"];
      }
      return GenericCalendarFeedDetails;
    },
    eventBarComponentForFeed(feedName) {
      if (
        this.calendar.calendarFeeds &&
        feedName &&
        Object.keys(calendarFeedEventBarComponents).includes(
          feedName + "eventbar",
        )
      ) {
        return calendarFeedEventBarComponents[feedName + "eventbar"];
      }
      return GenericCalendarFeedEventBar;
    },
    updateMinTime() {
      // Set the minimum time of the calendar
      const visibileEvents = this.events.filter((event) => {
        return (
          event.endDateTime.startOf("day") >=
            this.rangeDateTime.start.startOf("day") &&
          event.startDateTime.startOf("day") <=
            this.rangeDateTime.end.startOf("day")
        );
      });
      const minuteTimes = visibileEvents.map((event) =>
        this.getMinutesAfterMidnight(event.startDateTime),
      );

      let minTime =
        minuteTimes.length > 0 ? Math.min.apply(Math, minuteTimes) : 0;

      // instead of first time take the previous full hour
      minTime = Math.floor(Math.max(0, minTime - 1) / 60) * 60;

      this.firstTime = minTime;

      // When events are loaded, scroll once
      if (!this.scrolled && minuteTimes.length > 0) {
        this.scrollToTime();
      }
    },
    getMinutesAfterMidnight(date) {
      return 60 * date.hour + date.minute;
    },
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
    setCalendarRange({ start, end }) {
      this.range.start = start;
      this.range.end = end;
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
            let keepEvents = calendarFeed.events.filter(
              (event) =>
                this.$parseISODate(event.end) < start ||
                this.$parseISODate(event.start) > end,
            );

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
      this.title = this.$refs.calendar.title;

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
    getCurrentTime() {
      return this.cal
        ? this.cal.times.now.hour * 60 + this.cal.times.now.minute
        : 0;
    },
    scrollToTime() {
      let first;

      switch (this.scrollTarget) {
        case "first": {
          first = this.firstTime;
          break;
        }
        case "current":
        default: {
          const time = this.getCurrentTime();
          first = Math.max(0, time - (time % 30) - 30);
          break;
        }
      }

      if (this.startWithFirstTime) {
        first = first - this.firstTime;
      }

      this.cal.scrollToTime(first);

      this.scrolled = true;
    },
    updateTime() {
      // TODO: is this destroyed when unloading?
      setInterval(() => this.cal.updateTimes(), 60 * 1000);
    },
    clearDaysWithHiddenEvents() {
      this.daysWithHiddenEvents = {};
    },
  },
  mounted() {
    this.ready = true;
    this.$refs.calendar.move(0);
    this.updateTime();
  },
};
</script>

<style lang="scss">
.v-current-time {
  height: 2px;
  background-color: #ea4335;
  position: absolute;
  left: -1px;
  right: 0;
  pointer-events: none;

  &.first::before {
    content: "";
    position: absolute;
    background-color: #ea4335;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-top: -5px;
    margin-left: -6.5px;
  }
}
</style>
