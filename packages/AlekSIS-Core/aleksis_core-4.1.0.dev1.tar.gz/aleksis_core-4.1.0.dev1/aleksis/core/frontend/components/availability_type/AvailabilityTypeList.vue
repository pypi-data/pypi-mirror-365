<script setup>
import CRUDList from "../generic/CRUDList.vue";
import ColorField from "../generic/forms/ColorField.vue";
</script>

<template>
  <c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="availability_types.inline_list.create"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    item-title-attribute="description"
    :enable-edit="true"
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on, isCreate }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          required
          :rules="$rules().required.build()"
        ></v-text-field>
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #shortName.field="{ attrs, on, isCreate }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          required
          :rules="$rules().required.build()"
        ></v-text-field>
      </div>
    </template>

    <template #description="{ item }">
      {{ item.description ? item.description : "–" }}
    </template>

    <template #free="{ item }">
      <v-switch inset :input-value="item.free" disabled />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #free.field="{ attrs, on }">
      <v-switch
        v-bind="attrs"
        v-on="on"
        inset
        :false-value="false"
        :true-value="true"
        :hint="$t('availability_types.inline_list.free.help_text')"
        persistent-hint
      />
    </template>

    <template #public="{ item }">
      <v-switch inset :input-value="item.public" disabled />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #public.field="{ attrs, on }">
      <v-switch
        v-bind="attrs"
        v-on="on"
        inset
        :false-value="false"
        :true-value="true"
        :hint="$t('availability_types.inline_list.public.help_text')"
        persistent-hint
      />
    </template>

    <template #color="{ item }">
      <v-chip v-if="item.color" :color="item.color" outlined>{{
        item.color
      }}</v-chip>
      <template v-else> – </template>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #color.field="{ attrs, on }">
      <color-field v-bind="attrs" v-on="on" />
    </template>
  </c-r-u-d-list>
</template>

<script>
import {
  availabilityTypes,
  createAvailabilityTypes,
  deleteAvailabilityTypes,
  updateAvailabilityTypes,
} from "./availabilityType.graphql";

import formRulesMixin from "../../mixins/formRulesMixin";

export default {
  name: "AvailabilityTypeList",
  mixins: [formRulesMixin],
  data() {
    return {
      headers: [
        {
          text: this.$t("availability_types.inline_list.name"),
          value: "name",
        },
        {
          text: this.$t("availability_types.inline_list.short_name"),
          value: "shortName",
        },
        {
          text: this.$t("availability_types.inline_list.description"),
          value: "description",
          cols: 12,
        },
        {
          text: this.$t("availability_types.inline_list.free.label"),
          value: "free",
          cols: 12,
        },
        {
          text: this.$t("availability_types.inline_list.public.label"),
          value: "public",
          cols: 12,
        },
        {
          text: this.$t("availability_types.inline_list.color"),
          value: "color",
          cols: 12,
        },
      ],
      i18nKey: "availability_types.inline_list",
      gqlQuery: availabilityTypes,
      gqlCreateMutation: createAvailabilityTypes,
      gqlPatchMutation: updateAvailabilityTypes,
      gqlDeleteMutation: deleteAvailabilityTypes,
      defaultItem: {
        name: "",
        shortName: "",
        free: false,
        public: true,
        color: "",
      },
    };
  },
};
</script>

<style scoped></style>
