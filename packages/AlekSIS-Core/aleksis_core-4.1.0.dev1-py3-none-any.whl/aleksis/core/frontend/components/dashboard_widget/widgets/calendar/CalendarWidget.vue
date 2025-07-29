<script>
import widgetMixin from "../widgetMixin";
import Calendar from "../../../calendar/Calendar.vue";
import CalendarControlBar from "../../../calendar/CalendarControlBar.vue";

export default {
  name: "CalendarWidget",
  components: { CalendarControlBar, Calendar },
  mixins: [widgetMixin],
  computed: {
    feeds() {
      return JSON.parse(this.context).selected_calendars.map((calName) => ({
        name: calName,
      }));
    },
  },
  mounted() {
    this.$refs.calendar.setCalendarType("day");
  },
};
</script>

<template>
  <v-card>
    <v-card-title>
      {{ widget.title }}
    </v-card-title>
    <v-card-text>
      <div class="d-flex mb-3 justify-center">
        <!-- Control bar with prev, next and today buttons -->
        <calendar-control-bar
          @prev="$refs.calendar.prev()"
          @next="$refs.calendar.next()"
          @today="$refs.calendar.setCalendarFocus('')"
        />
      </div>

      <!-- Actual calendar -->
      <calendar
        :calendar-feeds="feeds"
        ref="calendar"
        scroll-target="current"
      />
    </v-card-text>
  </v-card>
</template>
