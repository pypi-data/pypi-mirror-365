<script>
import CRUDList from "../generic/CRUDList.vue";
import ForeignKeyField from "../generic/forms/ForeignKeyField.vue";
import RoleChip from "../role/RoleChip.vue";

import {
  groupTypes,
  createGroupTypes,
  deleteGroupTypes,
  updateGroupTypes,
} from "./groupType.graphql";
import { roles } from "../role/role.graphql";
import formRulesMixin from "../../mixins/formRulesMixin";

export default {
  name: "GroupType",
  components: { CRUDList, ForeignKeyField, RoleChip },
  mixins: [formRulesMixin],
  data() {
    return {
      allowedInformationChoices: [
        {
          value: "personal_details",
          name: this.$t(
            "group.group_type.allowed_information.personal_details",
          ),
        },
        {
          value: "address",
          name: this.$t("group.group_type.allowed_information.address"),
        },
        {
          value: "contact_details",
          name: this.$t("group.group_type.allowed_information.contact_details"),
        },
        {
          value: "photo",
          name: this.$t("group.group_type.allowed_information.photo"),
        },
        {
          value: "avatar",
          name: this.$t("group.group_type.allowed_information.avatar"),
        },
        {
          value: "groups",
          name: this.$t("group.group_type.allowed_information.groups"),
        },
      ],
      headers: [
        {
          text: this.$t("group.group_type.name"),
          value: "name",
        },
        {
          text: this.$t("group.group_type.description"),
          value: "description",
        },
        {
          text: this.$t("group.group_type.owners_can_see_groups"),
          value: "ownersCanSeeGroups",
          hidden: true,
          cols: 12,
        },
        {
          text: this.$t("group.group_type.owners_can_see_members"),
          value: "ownersCanSeeMembers",
          hidden: true,
          cols: 12,
        },
        {
          text: this.$t(
            "group.group_type.owners_can_see_members_allowed_information",
          ),
          value: "ownersCanSeeMembersAllowedInformation",
          hidden: true,
        },
        {
          text: this.$t("group.group_type.additional_attributes"),
          value: "attributes",
          disableEdit: true,
        },
        {
          text: this.$t("group.group_type.available_roles"),
          value: "availableRoles",
        },
      ],
      i18nKey: "group.group_type",
      gqlQuery: groupTypes,
      gqlCreateMutation: createGroupTypes,
      gqlPatchMutation: updateGroupTypes,
      gqlDeleteMutation: deleteGroupTypes,
      defaultItem: {
        name: "",
        description: "",
      },
      role: {
        gqlQuery: roles,
        enableCreate: false,
        chips: true,
        fields: [
          {
            text: this.$t("role.name"),
            value: "name",
          },
          {
            text: this.$t("role.short_name"),
            value: "shortName",
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
      },
    };
  },
  methods: {
    getData({
      id,
      name,
      description,
      ownersCanSeeGroups,
      ownersCanSeeMembers,
      ownersCanSeeMembersAllowedInformation,
      availableRoles,
    }) {
      return {
        id,
        name,
        description,
        ownersCanSeeGroups,
        ownersCanSeeMembers,
        ownersCanSeeMembersAllowedInformation,
        availableRoles,
      };
    },
  },
};
</script>

<template>
  <c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    create-item-i18n-key="group.group_type.create"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :gql-delete-mutation="gqlDeleteMutation"
    :get-create-data="getData"
    :get-patch-data="getData"
    :default-item="defaultItem"
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
    <template #description.field="{ attrs, on, isCreate }">
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
    <template #ownersCanSeeGroups.field="{ attrs, on }">
      <v-switch
        v-bind="attrs"
        v-on="on"
        inset
        :false-value="false"
        :true-value="true"
      />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #ownersCanSeeMembers.field="{ attrs, on }">
      <v-switch
        v-bind="attrs"
        v-on="on"
        inset
        :false-value="false"
        :true-value="true"
      />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #ownersCanSeeMembersAllowedInformation.field="{ attrs, on }">
      <v-autocomplete
        v-bind="attrs"
        v-on="on"
        chips
        small-chips
        multiple
        item-value="value"
        item-text="name"
        :items="allowedInformationChoices"
      />
    </template>

    <template #attributes="{ item }">
      <v-chip
        class="mr-2 mb-1"
        small
        color="secondary"
        v-if="item.ownersCanSeeGroups"
      >
        <v-icon left small>mdi-check-circle-outline</v-icon>
        {{ $t("group.group_type.owners_can_see_groups") }}</v-chip
      >

      <v-chip
        class="mr-2 mb-1"
        small
        color="secondary"
        v-if="item.ownersCanSeeMembers"
      >
        <v-icon left small>mdi-check-circle-outline</v-icon>
        {{ $t("group.group_type.owners_can_see_members") }}
        <template v-if="item.ownersCanSeeMembersAllowedInformation.length > 0">
          {{
            $t("group.group_type.owners_can_see_members_including", {
              allowedInformation: item.ownersCanSeeMembersAllowedInformation
                .map((value) =>
                  $t(`group.group_type.allowed_information.${value}`),
                )
                .join(", "),
            })
          }}
        </template>
      </v-chip>
    </template>

    <template #availableRoles="{ item }">
      <role-chip
        v-for="r in item.availableRoles"
        :key="r.id"
        :role="r"
        class="mr-1"
      />
      <span v-if="item.availableRoles.length === 0">–</span>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #availableRoles.field="{ attrs, on }">
      <foreign-key-field
        v-bind="attrs"
        v-on="on"
        :fields="role.fields"
        :gql-query="role.gqlQuery"
        :enable-create="role.enableCreate"
        :chips="role.chips"
        multiple
      />
    </template>
  </c-r-u-d-list>
</template>

<style scoped></style>
