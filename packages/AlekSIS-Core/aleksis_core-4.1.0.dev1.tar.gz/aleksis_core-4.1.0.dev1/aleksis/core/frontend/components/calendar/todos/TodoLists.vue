<script setup>
import DateField from "../../generic/forms/DateField.vue";
import CreateButton from "../../generic/buttons/CreateButton.vue";
</script>

<template>
  <div>
    <v-row class="overflow-x-auto flex-nowrap slide-n-snap-x-container">
      <v-col
        v-for="feed in calendar.calendarFeeds"
        :key="feed.name"
        class="slide-n-snap-contained"
        cols="12"
        :sm="Math.max(6, 12 / calendar.calendarFeeds.length)"
      >
        <v-card>
          <v-card-title>
            {{ feed.verboseName }}
          </v-card-title>
          <v-list two-line>
            <template v-for="event in getNonCompletedTodos(feed.events)">
              <component
                :is="listItemComponentForFeed(feed.name)"
                @refreshCalendar="refresh()"
                :key="event.uid"
                :selected-event="event"
              />
            </template>
            <v-list-group no-action>
              <template #activator>
                <v-list-item-content>
                  <v-list-item-title>{{
                    $t("calendar.todos.show_completed", {
                      count: getCompletedTodos(feed.events).length,
                    })
                  }}</v-list-item-title>
                </v-list-item-content>
              </template>

              <template v-for="event in getCompletedTodos(feed.events)">
                <component
                  :is="listItemComponentForFeed(feed.name)"
                  @refreshCalendar="refresh()"
                  :key="event.uid"
                  :selected-event="event"
                />
              </template>
            </v-list-group>
          </v-list>

          <v-card-actions v-if="formComponentForFeed(feed.name)">
            <component
              :is="formComponentForFeed(feed.name)"
              @refreshCalendar="refresh()"
            >
              <template #activator="{ on, attrs }">
                <create-button
                  v-bind="attrs"
                  v-on="on"
                  color="secondary"
                  outlined
                />
              </template>
            </component>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import calendarMixin from "../calendarMixin.js";

import {
  calendarFeedFormComponents,
  calendarFeedListItemComponents,
} from "aleksisAppImporter";

export default {
  name: "TodoLists",
  mixins: [calendarMixin],
  props: {},
  methods: {
    getEditItem(event) {
      return event;
    },
    getEventTypeName(feed) {
      return feed.name
        .toLowerCase()
        .replace(/[-_][a-z]/g, (group) => group.slice(-1).toUpperCase());
    },
    formComponentForFeed(feedName) {
      if (
        this.calendar.calendarFeeds &&
        feedName &&
        Object.keys(calendarFeedFormComponents).includes(feedName + "form")
      ) {
        return calendarFeedFormComponents[feedName + "form"];
      }
      return null;
    },
    listItemComponentForFeed(feedName) {
      if (
        this.calendar.calendarFeeds &&
        feedName &&
        Object.keys(calendarFeedListItemComponents).includes(
          feedName + "listitem",
        )
      ) {
        return calendarFeedListItemComponents[feedName + "listitem"];
      }
      return null;
    },
    getNonCompletedTodos(events) {
      return events.filter((e) => e.percentComplete !== 100);
    },
    getCompletedTodos(events) {
      return events.filter((e) => e.percentComplete === 100);
    },
  },
  mounted() {
    this.fetch();
  },
};
</script>

<style>
.slide-n-snap-x-container {
  scroll-snap-type: x mandatory;
  /* scroll-snap-stop: always; */
}
.slide-n-snap-y-container {
  scroll-snap-type: y mandatory;
  /* scroll-snap-stop: always; */
}
.slide-n-snap-contained {
  scroll-snap-align: start;
}
</style>
