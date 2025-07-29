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
  <div>
    <message-box type="info">
      {{ $t("announcement.explanation") }}
    </message-box>
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
      <template #datetimeStart="{ item }">
        {{ $d($parseISODate(item.datetimeStart), "shortDateTime") }}
      </template>
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #datetimeStart.field="{ attrs, on, item }">
        <div aria-required="true">
          <date-time-field
            dense
            hide-details="auto"
            v-bind="attrs"
            v-on="on"
            required
            :max="item.datetimeEnd"
            :rules="$rules().required.build()"
          />
        </div>
      </template>

      <template #datetimeEnd="{ item }">
        {{ $d($parseISODate(item.datetimeEnd), "shortDateTime") }}
      </template>
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #datetimeEnd.field="{ attrs, on, item }">
        <div aria-required="true">
          <date-time-field
            dense
            hide-details="auto"
            v-bind="attrs"
            v-on="on"
            required
            :min="
              $parseISODate(item.datetimeStart).plus({ minutes: 1 }).toISO()
            "
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
              item.recipientPersons?.length === 0 && !item.isGlobal
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
              item.recipientGroups?.length === 0 && !item.isGlobal
                ? $rules().isNonEmpty.build()
                : []
            "
            multiple
          />
        </div>
      </template>

      <template #isGlobal="{ item }">
        <v-switch
          :input-value="item.isGlobal"
          disabled
          inset
          :false-value="false"
          :true-value="true"
        />
      </template>
      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #isGlobal.field="{ attrs, on, item }">
        <v-switch
          v-bind="attrs"
          v-on="on"
          inset
          :false-value="false"
          :true-value="true"
          :rules="
            item.recipientGroups?.length === 0 &&
            item.recipientPersons?.length === 0
              ? $rules().required.build()
              : []
          "
        />
        <div>{{ $t("announcement.is_global_hint") }}</div>
      </template>

      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #title.field="{ attrs, on }">
        <div aria-required="true">
          <v-text-field
            v-bind="attrs"
            v-on="on"
            required
            :rules="$rules().required.build()"
            :hint="$t('announcement.title_hint')"
            persistent-hint
          />
        </div>
      </template>

      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #description.field="{ attrs, on }">
        <v-textarea
          rows="1"
          auto-grow
          :hint="$t('announcement.description_hint')"
          persistent-hint
          v-bind="attrs"
          v-on="on"
        />
      </template>

      <!-- eslint-disable-next-line vue/valid-v-slot -->
      <template #priority.field="{ attrs, on, item }">
        <positive-small-integer-field
          :hint="$t('announcement.priority_hint')"
          persistent-hint
          v-bind="attrs"
          v-on="on"
        />

        <message-box type="info" v-if="item.datetimeStart">
          {{
            $t(
              item.isGlobal
                ? "announcement.notifications_global_hint"
                : "announcement.notifications_hint",
              { when: $d($parseISODate(item.datetimeStart), "shortDateTime") },
            )
          }}
        </message-box>
      </template>
    </c-r-u-d-list>
  </div>
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
          value: "datetimeStart",
          cols: 6,
        },
        {
          text: this.$t("announcement.valid_until"),
          value: "datetimeEnd",
          cols: 6,
        },
        {
          text: this.$t("announcement.recipient_groups"),
          value: "recipientGroups",
          cols: 6,
          hidden: true,
        },
        {
          text: this.$t("announcement.recipient_persons"),
          value: "recipientPersons",
          cols: 6,
          hidden: true,
        },
        {
          text: this.$t("announcement.is_global"),
          value: "isGlobal",
          cols: 12,
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
          hidden: true,
        },
        {
          text: this.$t("announcement.priority"),
          value: "priority",
          cols: 12,
        },
      ],
      i18nKey: "announcement",
      gqlQuery: announcements,
      gqlCreateMutation: createAnnouncements,
      gqlPatchMutation: patchAnnouncements,
      gqlDeleteMutation: deleteAnnouncements,
      defaultItem: {
        datetimeStart: DateTime.now()
          .startOf("minute")
          .toISO({ suppressSeconds: true }),
        datetimeEnd: DateTime.now()
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
