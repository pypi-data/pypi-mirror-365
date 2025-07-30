<script>
import CRUDList from "../generic/CRUDList.vue";

import { deleteGroups, groups } from "./groups.graphql";
import CreateButton from "../generic/buttons/CreateButton.vue";
import TableLink from "../generic/TableLink.vue";
import AvatarContent from "../person/AvatarContent.vue";
import GroupTypeSelect from "../group_type/GroupTypeSelect.vue";

export default {
  name: "Group",
  components: {
    AvatarContent,
    TableLink,
    CreateButton,
    CRUDList,
    GroupTypeSelect,
  },
  data() {
    return {
      headers: [
        {
          text: this.$t("group.avatar"),
          value: "avatarUrl",
          sortable: false,
        },
        {
          text: this.$t("group.short_name"),
          value: "shortName",
        },
        {
          text: this.$t("group.name"),
          value: "name",
        },
        {
          text: this.$t("group.group_type.title"),
          value: "groupType",
        },
        {
          text: this.$t("group.school_term"),
          value: "schoolTerm",
        },
      ],
      i18nKey: "group",
      gqlQuery: groups,
      gqlDeleteMutation: deleteGroups,
    };
  },
};
</script>

<template>
  <c-r-u-d-list
    :headers="headers"
    :i18n-key="i18nKey"
    :gql-query="gqlQuery"
    :gql-delete-mutation="gqlDeleteMutation"
    :enable-filter="true"
    item-attribute="name"
  >
    <template #createComponent>
      <create-button :to="{ name: 'core.createGroup' }" />
    </template>

    <template #filters="{ attrs, on }">
      <group-type-select
        v-bind="attrs('group_type')"
        v-on="on('group_type')"
        outlined
      />
    </template>

    <template #avatarUrl="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        <v-avatar class="my-1 me-2">
          <avatar-content :image-url="item.avatarUrl" contain />
        </v-avatar>
      </table-link>
    </template>

    <template #name="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        {{ item.name }}
      </table-link>
    </template>

    <template #shortName="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        {{ item.shortName }}
      </table-link>
    </template>

    <template #groupType="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        {{ item.groupType?.name || "–" }}
      </table-link>
    </template>

    <template #schoolTerm="{ item }">
      <table-link :to="{ name: 'core.group', params: { id: item.id } }">
        {{ item.schoolTerm?.name || "–" }}
      </table-link>
    </template>
  </c-r-u-d-list>
</template>
