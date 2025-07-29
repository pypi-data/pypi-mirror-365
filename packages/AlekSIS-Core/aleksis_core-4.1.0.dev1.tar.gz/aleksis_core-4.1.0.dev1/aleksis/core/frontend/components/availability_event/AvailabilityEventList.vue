<script setup>
import CRUDList from "../generic/CRUDList.vue";
import CreateButton from "../generic/buttons/CreateButton.vue";

import MainCalendarEventDialog from "../calendar/MainCalendarEventDialog.vue";
</script>

<template>
  <c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="availability_events.inline_list.create"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    item-title-attribute="description"
    :enable-edit="true"
  >
    <template #createComponent="{ attrs, on, editItem }">
      <main-calendar-event-dialog
        v-bind="attrs"
        v-on="on"
        :initial-selected-event="`availability-type-${editItem.availabilityType.id}`"
        :selectable-events="selectableEvents"
      >
        <template #activator="{ attrs, on }">
          <create-button v-bind="attrs" v-on="on" color="secondary" />
        </template>
      </main-calendar-event-dialog>
    </template>

    <template #availabilityType="{ item }">
      <v-chip
        class="ma-2"
        :color="
          item.availabilityType.color
            ? item.availabilityType.color
            : item.availabilityType.free
              ? 'green'
              : 'red'
        "
        outlined
      >
        <v-icon left>
          {{ getAvailabilityIcon(item) }}
        </v-icon>
        {{
          item.availabilityType.shortName === "f" ||
          item.availabilityType.shortName === "b"
            ? $t(
                `calendar.create_event.event_types.${item.availabilityType.shortName}`,
              )
            : item.availabilityType.name
        }}
      </v-chip>
    </template>

    <template #datetimeStart="{ item }">
      {{ getStartString(item) }}
    </template>

    <template #datetimeEnd="{ item }">
      {{ getEndString(item) }}
    </template>

    <template #recurrences="{ item }">
      {{ rRuleToText(item.recurrences) }}
    </template>

    <template #title="{ item }">
      {{ item.title ? item.title : "-" }}
    </template>

    <template #description="{ item }">
      {{ item.description ? item.description : "-" }}
    </template>
  </c-r-u-d-list>
</template>

<script>
import {
  myAvailabilityEvents,
  createAvailabilityEvents,
  deleteAvailabilityEvents,
  updateAvailabilityEvents,
} from "./availabilityEvent.graphql";

import { publicAvailabilityTypes } from "../availability_type/availabilityType.graphql";

import { DateTime } from "luxon";
import { RRule } from "rrule";

export default {
  name: "AvailabilityEventList",
  data() {
    return {
      headers: [
        {
          text: this.$t("availability_events.inline_list.availability_type"),
          value: "availabilityType",
        },
        {
          text: this.$t("availability_events.inline_list.date_start"),
          value: "datetimeStart",
        },
        {
          text: this.$t("availability_events.inline_list.date_end"),
          value: "datetimeEnd",
        },
        {
          text: this.$t("availability_events.inline_list.recurrences"),
          value: "recurrences",
        },
        {
          text: this.$t("availability_events.inline_list.title"),
          value: "title",
        },
        {
          text: this.$t("availability_events.inline_list.description"),
          value: "description",
        },
      ],
      availabilityChoices: [
        {
          text: this.$t("availability_events.inline_list.free"),
          value: true,
        },
        {
          text: this.$t("availability_events.inline_list.busy"),
          value: false,
        },
      ],
      i18nKey: "availability_events.inline_list",
      gqlQuery: myAvailabilityEvents,
      gqlCreateMutation: createAvailabilityEvents,
      gqlPatchMutation: updateAvailabilityEvents,
      gqlDeleteMutation: deleteAvailabilityEvents,
      defaultItem: {
        description: "",
        free: true,
        datetimeStart: DateTime.now()
          .startOf("minute")
          .toISO({ suppressSeconds: true }),
        datetimeEnd: DateTime.now()
          .startOf("minute")
          .toISO({ suppressSeconds: true }),
        recurrences: "",
      },
      required: [(value) => !!value || this.$t("forms.errors.required")],
      radioButtonGroupRequired: [
        (value) => value !== null || this.$t("forms.errors.required"),
      ],
      rruleFrequencies: [
        {
          freq: RRule.DAILY,
          text: this.$t("forms.recurrence.frequencies.daily"),
        },
        {
          freq: RRule.WEEKLY,
          text: this.$t("forms.recurrence.frequencies.weekly"),
        },
        {
          freq: RRule.MONTHLY,
          text: this.$t("forms.recurrence.frequencies.monthly"),
        },
        {
          freq: RRule.YEARLY,
          text: this.$t("forms.recurrence.frequencies.yearly"),
        },
      ],
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
    getAvailabilityIcon(item) {
      return item.availabilityType.free
        ? "mdi-calendar-check-outline"
        : "mdi-calendar-remove-outline";
    },
    rRuleToText(rfcString) {
      if (rfcString) {
        const rRule = RRule.fromString(rfcString);
        let recurrence = this.rruleFrequencies.find(
          (r) => r.freq === rRule.options.interval,
        ).text;
        if (rRule.options.until) {
          recurrence += `, ${this.$t("availability_events.recurrences.until")} ${this.$d(
            rRule.options.until,
            "short",
          )}`;
        }
        return recurrence;
      }
      return this.$t("availability_events.recurrences.none");
    },
    getStartString(event) {
      if (event.datetimeStart) {
        return this.$d(this.$parseISODate(event.datetimeStart), "longNumeric");
      } else if (event.dateStart) {
        return this.$d(this.$parseISODate(event.dateStart));
      }
    },
    getEndString(event) {
      if (event.datetimeEnd) {
        return this.$d(this.$parseISODate(event.datetimeEnd), "longNumeric");
      } else if (event.dateEnd) {
        return this.$d(this.$parseISODate(event.dateEnd));
      }
    },
  },
  computed: {
    selectableEvents() {
      return this.availabilityTypes.map(
        (type) => `availability-type-${type.id}`,
      );
    },
  },
};
</script>

<style scoped></style>
