<script setup>
import CalendarEventDialog from "./CalendarEventDialog.vue";
import CollapseTriggerButton from "../generic/buttons/CollapseTriggerButton.vue";
import PersonField from "../generic/forms/PersonField.vue";
import GroupField from "../generic/forms/GroupField.vue";
import DateTimeField from "../generic/forms/DateTimeField.vue";
import PercentCompleteField from "./personal_todo/PercentCompleteField.vue";
</script>

<template>
  <calendar-event-dialog
    v-bind="$attrs"
    v-on="$listeners"
    :events="events"
    :title-required="!isAvailabilityEvent"
    @selectedEvent="selectedEvent = $event"
  >
    <template #activator="{ attrs, on }">
      <slot name="activator" v-bind="{ attrs, on, events }" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #description.field="{ attrs, on }">
      <v-textarea rows="1" auto-grow v-bind="attrs" v-on="on" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #location.field="{ attrs, on }">
      <v-slide-y-reverse-transition appear>
        <v-text-field v-bind="attrs" v-on="on" />
      </v-slide-y-reverse-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #persons.field="{ attrs, on }">
      <v-slide-y-reverse-transition appear>
        <person-field
          v-if="
            checkPermission('core.create_personal_event_with_invitations_rule')
          "
          multiple
          v-bind="attrs"
          v-on="on"
        />
      </v-slide-y-reverse-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #groups.field="{ attrs, on }">
      <v-slide-y-reverse-transition appear>
        <group-field
          v-if="
            checkPermission('core.create_personal_event_with_invitations_rule')
          "
          multiple
          v-bind="attrs"
          v-on="on"
        />
      </v-slide-y-reverse-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #percentComplete.field="{ attrs, on, item }">
      <v-slide-y-reverse-transition appear>
        <percent-complete-field v-bind="attrs" v-on="on" />
      </v-slide-y-reverse-transition>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #completed.field="{ attrs, on, item }">
      <v-slide-y-reverse-transition appear>
        <date-time-field
          v-show="item.percentComplete === 100"
          dense
          hide-details="auto"
          v-bind="attrs"
          v-on="on"
        />
      </v-slide-y-reverse-transition>
    </template>
  </calendar-event-dialog>
</template>

<script>
import { DateTime } from "luxon";

import {
  createPersonalEvents,
  updatePersonalEvents,
} from "./personal_event/personalEvent.graphql";

import {
  createPersonalTodos,
  updatePersonalTodos,
} from "./personal_todo/personalTodo.graphql";

import {
  createAvailabilityEvents,
  updateAvailabilityEvents,
} from "../availability_event/availabilityEvent.graphql";

import { publicAvailabilityTypes } from "../availability_type/availabilityType.graphql";

import permissionsMixin from "../../mixins/permissions.js";

export default {
  name: "MainCalendarEventDialog",
  extends: "CalendarEventDialog",
  mixins: [permissionsMixin],
  data() {
    return {
      selectedEvent: undefined,
      availabilityTypes: [],
    };
  },
  apollo: {
    availabilityTypes: {
      query: publicAvailabilityTypes,
      update(data) {
        return data.items;
      },
    },
  },
  methods: {
    personalTodoFilter(item) {
      if (item.percentComplete !== 100) {
        item.completed = null;
      }

      return item;
    },
  },
  computed: {
    isAvailabilityEvent() {
      return (
        typeof this.selectedEvent == "string" &&
        this.selectedEvent.startsWith("availability-type-")
      );
    },
    events() {
      let events = {
        personalEvent: {
          textKey: "calendar.create_event.event_types.personal_event",
          iconText: "mdi-calendar-account-outline",
          color: "primary",
          createMutation: createPersonalEvents,
          updateMutation: updatePersonalEvents,
          fields: {
            description: {
              default: undefined,
              cols: 12,
            },
            location: {
              default: undefined,
              cols: 12,
              textKey: "calendar.create_event.personal_events.location",
            },
            persons: {
              default: [],
              cols: 6,
              textKey: "calendar.create_event.personal_events.persons",
            },
            groups: {
              default: [],
              cols: 6,
              textKey: "calendar.create_event.personal_events.groups",
            },
          },
        },
        personalTodo: {
          textKey: "calendar.create_event.event_types.personal_todo",
          createMutation: createPersonalTodos,
          updateMutation: updatePersonalTodos,
          fields: {
            datetimeEnd: {
              default: DateTime.now()
                .startOf("minute")
                .plus({ hours: 1 })
                .toISO({ suppressSeconds: true }),
              textKey: "calendar.create_event.personal_todos.due",
              cols: 6,
            },
            description: {
              default: undefined,
              cols: 12,
            },
            location: {
              default: undefined,
              cols: 12,
              textKey: "calendar.create_event.personal_todos.location",
            },
            persons: {
              default: [],
              cols: 6,
              textKey: "calendar.create_event.personal_todos.persons",
            },
            groups: {
              default: [],
              cols: 6,
              textKey: "calendar.create_event.personal_todos.groups",
            },
            percentComplete: {
              default: 0,
              cols: 12,
              textKey: "calendar.create_event.personal_todos.percent_completed",
            },
            completed: {
              default: DateTime.now(),
              cols: 12,
              textKey: "calendar.create_event.personal_todos.completed",
            },
          },
          filter: this.personalTodoFilter,
        },
      };

      this.availabilityTypes.forEach((type) => {
        events[`availability-type-${type.id}`] = {
          textKey:
            type.shortName === "f" || type.shortName === "b"
              ? `calendar.create_event.event_types.${type.shortName}`
              : type.name,
          iconText:
            {
              f: "mdi-calendar-check-outline",
              b: "mdi-calendar-remove-outline",
            }[type.shortName] || "mdi-calendar-clock",
          color:
            {
              f: "success",
              b: "error",
            }[type.shortName] || "secondary",
          createMutation: createAvailabilityEvents,
          updateMutation: updateAvailabilityEvents,
          fields: {
            description: {
              default: undefined,
              cols: 12,
            },
          },
          filter: (object) => ({ ...object, availabilityType: type.id }),
        };
      });

      return events;
    },
  },
  mounted() {
    this.addPermissions(["core.create_personal_event_with_invitations_rule"]);
  },
};
</script>
