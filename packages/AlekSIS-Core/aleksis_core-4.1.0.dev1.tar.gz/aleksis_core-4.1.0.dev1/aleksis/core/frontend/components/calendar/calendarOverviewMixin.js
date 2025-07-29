/**
 * Mixin for use with calendar components.
 */

const calendarOverviewMixin = {
  data() {
    return {
      calendarFocus: "",
      calendarType: "week",
      calendarView: "calendar",
    };
  },
  methods: {
    setCalendarFocus(val) {
      this.calendarFocus = val;
    },
    setCalendarType(val) {
      this.calendarType = val;
    },
  },
  watch: {
    calendarFocus(val) {
      this.$refs.calendar.setCalendarFocus(val);
    },
    calendarType(val) {
      this.$refs.calendar.setCalendarType(val);
    },
  },
};

export default calendarOverviewMixin;
