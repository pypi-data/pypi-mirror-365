<script>
export default {
  name: "CalendarViewSelect",
  props: {
    value: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      innerValue: this.value,
      availableCalendarViews: [
        {
          type: "calendar",
          translationKey: "calendar.views.calendar",
          icon: "mdi-calendar-multiple",
          iconActive: "mdi-calendar-multiple",
        },
        {
          type: "todos",
          translationKey: "calendar.views.todos",
          icon: "mdi-checkbox-multiple-marked-circle-outline",
          iconActive: "mdi-checkbox-multiple-marked-circle-outline",
        },
      ],
    };
  },
  watch: {
    value(val) {
      this.innerValue = val;
    },
    innerValue(val) {
      this.$emit("input", val);
    },
  },
  methods: {
    nameForMenu(item) {
      return this.$t(item.translationKey);
    },
  },
};
</script>

<template>
  <v-btn-toggle dense mandatory v-model="innerValue" class="mx-2">
    <v-btn
      v-for="calendarView in availableCalendarViews"
      :value="calendarView.type"
      :key="calendarView.type"
      :aria-label="nameForMenu(calendarView)"
    >
      <v-icon v-if="$vuetify.breakpoint.smAndDown">{{
        calendarView.type === innerValue
          ? calendarView.iconActive
          : calendarView.icon
      }}</v-icon>
      <span class="hidden-sm-and-down">{{ nameForMenu(calendarView) }}</span>
    </v-btn>
  </v-btn-toggle>
</template>
