<script setup>
import PersonForm from "./PersonForm.vue";
</script>

<template>
  <div>
    <v-btn
      v-if="person.canEdit"
      color="primary"
      :to="{
        name: 'core.personById',
        params: { id: person.id },
        query: { _ui_action: 'edit' },
      }"
    >
      <v-icon left>$edit</v-icon>
      {{ $t("actions.edit") }}
    </v-btn>
    <v-btn
      v-if="person.canChangePersonPreferences"
      color="secondary"
      outlined
      text
      :to="{
        name: 'core.preferencesPersonByPk',
        params: { pk: person.id },
      }"
    >
      <v-icon left>$preferences</v-icon>
      {{ $t("preferences.person.change_preferences") }}
    </v-btn>

    <button-menu
      v-if="
        person.canImpersonatePerson ||
        person.canInvitePerson ||
        person.canDelete
      "
      icon-only
      text-translation-key="actions.more_actions"
    >
      <v-list-item
        v-if="person.canImpersonatePerson"
        :to="{
          name: 'impersonate.impersonateByUserPk',
          params: { uid: person.userid },
          query: { next: $route.path },
        }"
      >
        <v-list-item-icon>
          <v-icon>mdi-account-box-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            {{ $t("person.impersonation.impersonate") }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        v-if="person.canInvitePerson"
        :to="{
          name: 'core.invitePerson',
          params: { id: person.id },
        }"
      >
        <v-list-item-icon>
          <v-icon>mdi-account-plus-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            {{ $t("person.invite") }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        v-if="person.canDelete"
        @click="showDeleteConfirm = true"
        class="error--text"
      >
        <v-list-item-icon>
          <v-icon color="error">$deleteContent</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            {{ $t("person.delete") }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </button-menu>
    <delete-dialog
      v-model="showDeleteConfirm"
      :gql-delete-mutation="deleteMutation"
      item-attribute="fullName"
      :items="[person]"
      @confirm="
        $router.push({
          name: 'core.persons',
        })
      "
    >
      <template #title>
        {{ $t("person.confirm_delete") }}
      </template>
    </delete-dialog>
  </div>
</template>

<script>
import { deletePersons } from "./personList.graphql";
import DeleteDialog from "../generic/dialogs/DeleteDialog.vue";

export default {
  name: "PersonActions",
  components: { DeleteDialog },
  props: {
    person: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      showDeleteConfirm: false,
      deleteMutation: deletePersons,
    };
  },
};
</script>

<style scoped></style>
