<script>
import CRUDList from "../generic/CRUDList.vue";

import CreateButton from "../generic/buttons/CreateButton.vue";
import EditButton from "../generic/buttons/EditButton.vue";
import InviteButton from "../generic/buttons/InviteButton.vue";
import SexSelect from "../generic/forms/SexSelect.vue";
import GroupChip from "../group/GroupChip.vue";
import TableLink from "../generic/TableLink.vue";

import personCRUDMixin from "../../mixins/personCRUDMixin.js";

export default {
  name: "Person",
  components: {
    TableLink,
    GroupChip,
    SexSelect,
    CreateButton,
    EditButton,
    InviteButton,
    CRUDList,
  },
  mixins: [personCRUDMixin],
  data() {
    return {
      headers: [
        {
          text: this.$t("person.first_name"),
          value: "firstName",
        },
        {
          text: this.$t("person.last_name"),
          value: "lastName",
        },
        {
          text: this.$t("person.short_name"),
          value: "shortName",
        },
        {
          text: this.$t("person.primary_group"),
          value: "primaryGroup",
        },
      ],
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
    :gql-patch-mutation="gqlPatchMutation"
    :gql-create-mutation="gqlCreateMutation"
    :enable-filter="true"
    item-attribute="fullName"
  >
    <template #createComponent="{ attrs, on, createMode }">
      <invite-button :to="{ name: 'core.invite_person' }" />
      <create-button
        color="secondary"
        :to="{
          name: 'core.persons',
          query: { _ui_action: 'create' },
        }"
        :disabled="$route.query._ui_action === 'create'"
      />
    </template>

    <template #filters="{ attrs, on }">
      <v-text-field
        v-bind="attrs('name')"
        v-on="on('name')"
        :label="$t('person.name')"
      />
      <v-text-field
        v-bind="attrs('contact')"
        v-on="on('contact')"
        :label="$t('person.details')"
      />
      <sex-select
        v-bind="attrs('sex')"
        v-on="on('sex')"
        :label="$t('person.sex.field')"
      />
    </template>

    <template #lastName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.lastName }}
      </table-link>
    </template>

    <template #firstName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.firstName }}
      </table-link>
    </template>

    <template #shortName="{ item }">
      <table-link :to="{ name: 'core.personById', params: { id: item.id } }">
        {{ item.shortName }}
      </table-link>
    </template>

    <template #primaryGroup="{ item }">
      <group-chip :group="item.primaryGroup" v-if="item.primaryGroup" />
      <span v-else>–</span>
    </template>

    <template #actions="{ item }">
      <edit-button
        v-if="'canEdit' in item && item.canEdit"
        icon
        color="secondary"
        :to="{
          name: 'core.personById',
          params: { id: item.id },
          query: { _ui_action: 'edit' },
        }"
      />
    </template>
  </c-r-u-d-list>
</template>
