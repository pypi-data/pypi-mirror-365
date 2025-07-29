<template>
  <div>
    <div
      class="mx-2 mb-2 text-center"
      v-if="$refs.calendar && $vuetify.breakpoint.smAndDown"
    >
      {{ $refs.calendar.title }}
    </div>

    <div class="d-flex mb-3 justify-space-between">
      <!-- Control bar with prev, next and today buttons -->
      <calendar-control-bar
        @prev="$refs.calendar.prev()"
        @next="$refs.calendar.next()"
        @today="calendarFocus = ''"
      />

      <!-- Calendar title with current calendar time range -->
      <div class="mx-2" v-if="$refs.calendar && $vuetify.breakpoint.mdAndUp">
        {{ $refs.calendar.title }}
      </div>

      <calendar-type-select v-model="calendarType" />
    </div>

    <!-- Actual calendar -->
    <calendar
      :calendar-feeds="calendarFeeds"
      @changeCalendarFocus="handleChangeCalendarFocus"
      @changeCalendarType="handleChangeCalendarType"
      v-bind="$attrs"
      ref="calendar"
      :start-with-first-time="startWithFirstTime"
      :calendar-days-of-week="calendarDaysOfWeek"
      :scroll-target="scrollTarget"
    />
  </div>
</template>

<script>
import CalendarControlBar from "./CalendarControlBar.vue";
import CalendarTypeSelect from "./CalendarTypeSelect.vue";
import Calendar from "./Calendar.vue";
import calendarOverviewMixin from "./calendarOverviewMixin";
export default {
  name: "CalendarWithControls",
  components: {
    Calendar,
    CalendarTypeSelect,
    CalendarControlBar,
  },
  mixins: [calendarOverviewMixin],
  emits: ["changeCalendarFocus", "changeCalendarType", "calendarReady"],
  props: {
    calendarFeeds: {
      type: Array,
      required: true,
    },
    startWithFirstTime: {
      type: Boolean,
      required: false,
      default: () => true,
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
  },
  methods: {
    handleChangeCalendarFocus(val) {
      this.setCalendarFocus(val);
      this.$emit("changeCalendarFocus", val);
    },
    handleChangeCalendarType(val) {
      this.setCalendarType(val);
      this.$emit("changeCalendarType", val);
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.$emit("calendarReady");
    });
  },
};
</script>
