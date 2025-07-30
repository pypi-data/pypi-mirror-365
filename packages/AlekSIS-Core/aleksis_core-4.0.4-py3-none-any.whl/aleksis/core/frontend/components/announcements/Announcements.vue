<script setup>
import CRUDList from "../generic/CRUDList.vue";
import DateTimeField from "../generic/forms/DateTimeField.vue";
import GroupChip from "../group/GroupChip.vue";
import GroupField from "../generic/forms/GroupField.vue";
import PersonChip from "../person/PersonChip.vue";
import PersonField from "../generic/forms/PersonField.vue";
import PositiveSmallIntegerField from "../generic/forms/PositiveSmallIntegerField.vue";
</script>

<template>
  <c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    item-attribute="title"
    :enable-edit="true"
  >
    <template #validFrom="{ item }">
      {{ $d($parseISODate(item.validFrom), "shortDateTime") }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #validFrom.field="{ attrs, on, item }">
      <div aria-required="true">
        <date-time-field
          dense
          hide-details="auto"
          v-bind="attrs"
          v-on="on"
          required
          :max="item.validUntil"
          :rules="$rules().required.build()"
        />
      </div>
    </template>

    <template #validUntil="{ item }">
      {{ $d($parseISODate(item.validUntil), "shortDateTime") }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #validUntil.field="{ attrs, on, item }">
      <div aria-required="true">
        <date-time-field
          dense
          hide-details="auto"
          v-bind="attrs"
          v-on="on"
          required
          :min="$parseISODate(item.validFrom).plus({ minutes: 1 }).toISO()"
          :rules="$rules().required.build()"
        />
      </div>
    </template>

    <template #recipientGroups="{ item }">
      <group-chip
        v-for="group in item.recipientGroups"
        :key="group.id"
        :group="group"
        format="short"
        class="mr-1"
      />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #recipientGroups.field="{ attrs, on, item }">
      <div :aria-required="item.recipientPersons?.length === 0">
        <group-field
          v-bind="attrs"
          v-on="on"
          :required="item.recipientPersons?.length === 0"
          :rules="
            item.recipientPersons?.length === 0
              ? $rules().isNonEmpty.build()
              : []
          "
          multiple
        />
      </div>
    </template>

    <template #recipientPersons="{ item }">
      <person-chip
        v-for="person in item.recipientPersons"
        :key="person.id"
        :person="person"
        class="mr-1"
      />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #recipientPersons.field="{ attrs, on, item }">
      <div :aria-required="item.recipientGroups?.length === 0">
        <person-field
          v-bind="attrs"
          v-on="on"
          :required="item.recipientGroups?.length === 0"
          :rules="
            item.recipientGroups?.length === 0
              ? $rules().isNonEmpty.build()
              : []
          "
          multiple
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #title.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          required
          :rules="$rules().required.build()"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #description.field="{ attrs, on }">
      <v-textarea rows="1" auto-grow v-bind="attrs" v-on="on" />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #priority.field="{ attrs, on }">
      <positive-small-integer-field v-bind="attrs" v-on="on" />
    </template>
  </c-r-u-d-list>
</template>

<script>
import {
  announcements,
  createAnnouncements,
  deleteAnnouncements,
  patchAnnouncements,
} from "./announcements.graphql";

import formRulesMixin from "../../mixins/formRulesMixin";
import { DateTime } from "luxon";

export default {
  name: "Announcements",
  mixins: [formRulesMixin],
  data() {
    return {
      headers: [
        {
          text: this.$t("announcement.valid_from"),
          value: "validFrom",
          cols: 6,
        },
        {
          text: this.$t("announcement.valid_until"),
          value: "validUntil",
          cols: 6,
        },
        {
          text: this.$t("announcement.recipient_groups"),
          value: "recipientGroups",
          cols: 6,
        },
        {
          text: this.$t("announcement.recipient_persons"),
          value: "recipientPersons",
          cols: 6,
        },
        {
          text: this.$t("announcement.title"),
          value: "title",
          cols: 12,
        },
        {
          text: this.$t("announcement.description"),
          value: "description",
          cols: 12,
        },
        {
          text: this.$t("announcement.priority"),
          value: "priority",
          cols: 5,
        },
      ],
      i18nKey: "announcement",
      gqlQuery: announcements,
      gqlCreateMutation: createAnnouncements,
      gqlPatchMutation: patchAnnouncements,
      gqlDeleteMutation: deleteAnnouncements,
      defaultItem: {
        validFrom: DateTime.now()
          .startOf("minute")
          .toISO({ suppressSeconds: true }),
        validUntil: DateTime.now()
          .startOf("minute")
          .plus({ hours: 1 })
          .toISO({ suppressSeconds: true }),
        recipientGroups: [],
        recipientPersons: [],
        title: "",
        description: "",
      },
    };
  },
};
</script>
