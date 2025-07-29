<template>
  <base-calendar-feed-details v-bind="$props">
    <template #description="{ selectedEvent }">
      <v-divider
        inset
        v-if="selectedEvent.description && !withoutDescription"
      />

      <!--
            Description of the free/busy event
          -->
      <v-list-item v-if="selectedEvent.description && !withoutDescription">
        <v-list-item-icon>
          <v-icon color="primary">mdi-card-text-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-content style="white-space: pre-line">
          {{ selectedEvent.description }}
        </v-list-item-content>
      </v-list-item>

      <!--
            Linked groups of the free/busy event
        -->
      <v-list-item v-if="selectedEvent.meta.groups.length">
        <v-list-item-icon>
          <v-icon color="primary">mdi-account-group-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            <v-chip
              v-for="group in selectedEvent.meta.groups"
              :key="group.id"
              label
              outlined
              >{{ group.name }}</v-chip
            >
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <!--
            Linked persons of the free/busy event
        -->
      <v-list-item v-if="selectedEvent.meta.persons.length">
        <v-list-item-icon>
          <v-icon color="primary">mdi-account-outline </v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            <v-chip
              v-for="person in selectedEvent.meta.persons"
              :key="person.id"
              label
              outlined
              >{{ person.full_name }}</v-chip
            >
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </template>
  </base-calendar-feed-details>
</template>

<script>
import calendarFeedDetailsMixin from "../../../mixins/calendarFeedDetails.js";
import BaseCalendarFeedDetails from "../../calendar/BaseCalendarFeedDetails.vue";

export default {
  name: "Free_BusyDetails",
  components: {
    BaseCalendarFeedDetails,
  },
  mixins: [calendarFeedDetailsMixin],
};
</script>
