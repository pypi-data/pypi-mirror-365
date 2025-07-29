<script setup>
import TodoLists from "./todos/TodoLists.vue";
</script>

<template>
  <v-sheet class="mb-10">
    <main-calendar-event-dialog
      :initial-selected-event="presetEvent"
      @save="$refs.calendar.refresh()"
    >
      <template #activator="{ on, attrs, events }">
        <v-speed-dial v-model="fab" color="secondary" bottom fixed right>
          <template #activator>
            <create-button v-model="fab" color="secondary" fab large>
              <v-icon> {{ fabIcon }} </v-icon>
            </create-button>
          </template>

          <v-tooltip
            v-for="(value, event) in events"
            :key="`chip-${event}`"
            left
            :value="$vuetify.breakpoint.mobile"
            :nudge-left="$vuetify.breakpoint.mobile ? 20 : 0"
          >
            <template #activator="tooltipProps">
              <v-btn
                v-bind="tooltipProps.attrs"
                v-on="tooltipProps.on"
                fab
                small
                @click="handleCreate(event, on, $event)"
                :color="value.color"
              >
                <v-icon>
                  {{ value.iconText }}
                </v-icon>
              </v-btn>
            </template>
            <span>{{ $t(value.textKey) }}</span>
          </v-tooltip>
        </v-speed-dial>
      </template>
    </main-calendar-event-dialog>
    <v-row align="stretch" class="page-height flex-nowrap">
      <v-navigation-drawer
        v-show="calendarView === 'calendar'"
        :clipped="$vuetify.breakpoint.lgAndUp"
        hide-overlay
        disable-route-watcher
        v-model="sidebar"
        lg="3"
        xl="2"
        :floating="$vuetify.breakpoint.lgAndUp"
        class="pt-6"
        :temporary="$vuetify.breakpoint.mdAndDown"
        :app="$vuetify.breakpoint.mdAndDown"
      >
        <calendar-control-bar
          @prev="$refs.calendar.prev()"
          @next="$refs.calendar.next()"
          @today="calendarFocus = ''"
        />

        <!-- Mini date picker -->
        <v-date-picker
          @wheel.native.prevent="handleWheel"
          no-title
          v-model="calendarFocus"
          :first-day-of-week="1"
          full-width
        ></v-date-picker>

        <!-- Calendar select (only desktop) -->
        <v-list flat subheader>
          <v-subheader>
            {{ $t("calendar.my_calendars") }}
          </v-subheader>
          <calendar-select
            class="mb-4 overflow-auto"
            v-model="selectedCalendarFeedNames"
            :calendar-feeds="calendar.calendarFeeds"
            @input="storeActivatedCalendars"
          />
        </v-list>
        <template #append>
          <div class="pa-4 d-flex justify-center align-center">
            <v-spacer />
            <calendar-download-all-button
              v-if="calendar?.allFeedsUrl"
              :url="calendar.allFeedsUrl"
            />
            <v-spacer />
          </div>
        </template>
      </v-navigation-drawer>
      <v-col
        :lg="calendarView === 'calendar' ? 9 : 12"
        :xl="calendarView === 'calendar' ? 10 : 12"
        class="d-flex flex-column fill-height"
      >
        <div class="d-flex justify-space-between flex-wrap mb-2 align-center">
          <!-- Calendar title with current calendar time range -->
          <h2 v-if="$refs.calendar" v-show="calendarView === 'calendar'">
            <v-btn
              icon
              @click="sidebar = true"
              small
              v-if="$vuetify.breakpoint.mdAndDown"
            >
              <v-icon>mdi-menu</v-icon>
            </v-btn>
            {{ $refs.calendar.title }}
          </h2>

          <!-- Control bar with prev, next and today buttons -->
          <calendar-control-bar
            v-show="calendarView === 'calendar'"
            v-if="$vuetify.breakpoint.mdAndDown"
            @prev="$refs.calendar.prev()"
            @next="$refs.calendar.next()"
            @today="calendarFocus = ''"
            small
          />

          <v-spacer />

          <!-- Calendar type select (month, week, day) -->
          <calendar-type-select
            v-show="calendarView === 'calendar'"
            v-model="calendarType"
            class="mt-1 mt-md-0 mr-2"
          />

          <!-- Calendar view select (regular calendar, todos view) -->
          <calendar-view-select v-model="calendarView" class="mt-1 ma-md-0" />
        </div>
        <v-row class="overflow-auto calendar-height">
          <v-col class="fill-height">
            <!-- Actual calendar -->
            <calendar
              v-show="calendarView === 'calendar'"
              :calendar-feeds="selectedFeedsForCalendar"
              @changeCalendarFocus="setCalendarFocus"
              @changeCalendarType="setCalendarType"
              ref="calendar"
              height="100%"
              class="fill-height"
            />
            <!-- Todo lists -->
            <todo-lists
              v-show="calendarView === 'todos'"
              :calendar-feeds="todoFeeds"
            />
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-sheet>
</template>

<script>
import { DateTime } from "luxon";

import CalendarSelect from "./CalendarSelect.vue";

import CalendarControlBar from "./CalendarControlBar.vue";
import CalendarTypeSelect from "./CalendarTypeSelect.vue";
import CalendarViewSelect from "./CalendarViewSelect.vue";
import Calendar from "./Calendar.vue";
import CalendarDownloadAllButton from "./CalendarDownloadAllButton.vue";
import MainCalendarEventDialog from "./MainCalendarEventDialog.vue";
import calendarOverviewMixin from "./calendarOverviewMixin";
import calendarSelectedFeedsMixin from "./calendarSelectedFeedsMixin";

import CreateButton from "../generic/buttons/CreateButton.vue";

export default {
  name: "CalendarOverview",
  mixins: [calendarOverviewMixin, calendarSelectedFeedsMixin],
  components: {
    Calendar,
    CalendarTypeSelect,
    CalendarViewSelect,
    CalendarControlBar,
    CalendarSelect,
    CalendarDownloadAllButton,
    MainCalendarEventDialog,
    CreateButton,
  },
  methods: {
    handleCreate(calendarEvent, on, clickEvent) {
      this.presetEvent = calendarEvent;
      on.click(clickEvent);
    },
    handleWheel(event) {
      if (event.wheelDelta < 0) {
        this.$refs.calendar.next();
      } else {
        this.$refs.calendar.prev();
      }
    },
  },
  computed: {
    sidebar: {
      get() {
        return this.internalSidebar || this.$vuetify.breakpoint.lgAndUp;
      },
      set(value) {
        this.internalSidebar = value;
      },
    },
    fabIcon() {
      if (this.fab) {
        return "$close";
      }
      return "$plus";
    },
  },
  data() {
    return {
      internalSidebar: false,
      presetEvent: undefined,
      fab: false,
    };
  },
  mounted() {
    if (this.$route.name === "core.calendar_overview") {
      this.setCalendarFocus(DateTime.now().toISODate());
      this.setCalendarType(this.$vuetify.breakpoint.mdAndDown ? "day" : "week");
    } else {
      // If we are here, we have a date supplied via the route params
      this.setCalendarFocus(
        [
          this.$route.params.year,
          this.$route.params.month,
          this.$route.params.day,
        ].join("-"),
      );
      this.setCalendarType(this.$route.params.view);
    }
  },
  watch: {
    calendarFocus(newValue, oldValue) {
      // Do not redirect on first page load
      if (oldValue === "") return;

      const [year, month, day] = newValue.split("-");
      this.$router.push({
        name: "core.calendar_overview_with_params",
        params: {
          view: this.calendarType,
          year,
          month,
          day,
        },
      });
    },
    calendarType(newValue) {
      const [year, month, day] = this.calendarFocus.split("-");
      this.$router.push({
        name: "core.calendar_overview_with_params",
        params: {
          view: newValue,
          year,
          month,
          day,
        },
      });
    },
  },
};
</script>

<style scoped>
.page-height {
  /* not all browsers support dvh so we use vh as fallback */
  height: calc(98vh - 11rem);
  height: calc(100dvh - 11rem);
  overflow: auto;
}

.calendar-height {
  min-height: 400px;
}
</style>
