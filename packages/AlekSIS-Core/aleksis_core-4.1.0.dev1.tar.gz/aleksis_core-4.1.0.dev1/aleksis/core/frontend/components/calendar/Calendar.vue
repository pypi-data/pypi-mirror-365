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

import calendarMixin from "./calendarMixin.js";

import { Interval } from "luxon";

export default {
  name: "Calendar",
  mixins: [calendarMixin],
  props: {
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

      selectedElement: null,
      selectedOpen: false,

      firstTime: 1,
      scrolled: false,

      personByIdOrMe: {
        id: null,
        preferences: {
          daysOfWeek: [1, 2, 3, 4, 5, 6, 0],
        },
      },

      showAllAllDayEvents: false,
      daysWithHiddenEvents: {},

      ready: false,
    };
  },
  apollo: {
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
    internalCalendarType(val) {
      this.$emit("changeCalendarType", val);
    },
    internalCalendarFocus(val) {
      this.$emit("changeCalendarFocus", val);
    },
    selectedEvent(val) {
      this.$emit("selectEvent", val);
    },
    range: {
      handler() {
        this.updateMinTime();
        this.fetch();

        this.title = this.$refs.calendar.title;
      },
      deep: true,
    },
    events: {
      handler() {
        this.updateMinTime();
      },
      deep: true,
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
    setCalendarRange({ start, end }) {
      this.range.start = start;
      this.range.end = end;
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
