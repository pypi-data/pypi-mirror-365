<script>
import ColorField from "../generic/forms/ColorField.vue";
import InlineCRUDList from "../generic/InlineCRUDList.vue";
import RoleChip from "../role/RoleChip.vue";

import { roles, createRoles, deleteRoles, updateRoles } from "./role.graphql";
import formRulesMixin from "../../mixins/formRulesMixin";

export default {
  name: "Role",
  components: { ColorField, InlineCRUDList, RoleChip },
  mixins: [formRulesMixin],
  data() {
    return {
      headers: [
        {
          text: this.$t("role.name"),
          value: "name",
        },
        {
          text: this.$t("role.short_name"),
          value: "shortName",
        },
        {
          text: this.$t("role.reciprocal_name"),
          value: "reciprocalName",
        },
        {
          text: this.$t("role.ical_participation_role"),
          value: "icalParticipationRole",
        },
        {
          text: this.$t("role.vcard_related_type"),
          value: "vcardRelatedType",
        },
        {
          text: this.$t("role.fg_color"),
          value: "fgColor",
        },
        {
          text: this.$t("role.bg_color"),
          value: "bgColor",
        },
      ],
      i18nKey: "role",
      gqlQuery: roles,
      gqlCreateMutation: createRoles,
      gqlPatchMutation: updateRoles,
      gqlDeleteMutation: deleteRoles,
      defaultItem: {
        name: "",
        shortName: "",
        reciprocalName: "",
        fgColor: "",
        bgColor: "",
      },
    };
  },
};
</script>

<template>
  <inline-c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="role.create"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :default-item="defaultItem"
    enable-edit
  >
    <template #name="{ item }">
      <role-chip :role="item" />
    </template>

    <template #fgColor="{ item }">
      <v-chip :color="item.fgColor" outlined>{{ item.fgColor }}</v-chip>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #fgColor.field="{ attrs, on }">
      <color-field v-bind="attrs" v-on="on" />
    </template>

    <template #bgColor="{ item }">
      <v-chip :color="item.bgColor" outlined>{{ item.bgColor }}</v-chip>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #bgColor.field="{ attrs, on }">
      <color-field v-bind="attrs" v-on="on" />
    </template>
  </inline-c-r-u-d-list>
</template>

<style scoped></style>
