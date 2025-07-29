<script setup>
import PersonForm from "./PersonForm.vue";
import ConfirmDialog from "../generic/dialogs/ConfirmDialog.vue";
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
        person.canDelete ||
        person.canChangePassword ||
        person.canSendPasswordResetRequest
      "
      icon-only
      text-translation-key="actions.more_actions"
    >
      <v-list-item
        v-if="person.canImpersonatePerson && person.userid"
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

      <v-list-item
        v-if="
          person.userid && person.email && person.canSendPasswordResetRequest
        "
        @click="showConfirmPasswordReset = true"
        class="error--text"
      >
        <v-list-item-icon>
          <v-icon color="error">mdi-form-textbox-password</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            {{ $t("accounts.reset_password.button") }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>

      <v-list-item
        v-if="person.userid && person.canChangePassword"
        class="error--text"
        :to="{
          name: 'core.personById',
          params: { id: person.id },
          query: { _ui_action: 'change_password' },
        }"
      >
        <v-list-item-icon>
          <v-icon color="error">mdi-form-textbox-password</v-icon>
        </v-list-item-icon>
        <v-list-item-content>
          <v-list-item-title>
            {{ $t("accounts.change_password.action") }}
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
    <confirm-dialog
      v-model="showConfirmPasswordReset"
      @confirm="sendPasswortReset"
    >
      <template #title>
        {{ $t("accounts.reset_password.foreign_user.confirm.title") }}
      </template>
      <template #text>
        {{ $t("accounts.reset_password.foreign_user.confirm.message") }}
      </template>
    </confirm-dialog>
  </div>
</template>

<script>
import { deletePersons } from "./personList.graphql";
import DeleteDialog from "../generic/dialogs/DeleteDialog.vue";
import { requestPasswordReset } from "../account/passwordReset.graphql";

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
      showConfirmPasswordReset: false,
      deleteMutation: deletePersons,
    };
  },
  methods: {
    sendPasswortReset() {
      this.$apollo
        .mutate({
          mutation: requestPasswordReset,
          variables: {
            email: this.person.email,
          },
        })
        .then(() => {
          this.$toastSuccess(this.$t("accounts.reset_password.done.title"));
        })
        .catch((error) => {
          this.handleMutationError(error);
        })
        .finally(() => {
          this.handleLoading(false);
        });
    },
  },
};
</script>

<style scoped></style>
