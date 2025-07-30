<script setup>
import CRUDList from "../generic/CRUDList.vue";
import FileField from "../generic/forms/FileField.vue";
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
    :enable-edit="true"
    @create="$apollo.queries.initOauthApplication.skip = false"
    @save="handleSave"
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on }">
      <v-text-field
        v-bind="attrs"
        v-on="on"
        filled
        required
        :rules="$rules().required.build()"
      />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #clientId.field="{ attrs, on }">
      <v-text-field v-bind="attrs" v-on="on" filled readonly />
    </template>

    <template #clientSecret="{ item }">
      <div class="client_secret">
        {{ item.clientSecret }}
      </div>
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #clientSecret.field="{ attrs, on, isCreate }">
      <v-text-field
        v-bind="attrs"
        v-on="on"
        filled
        readonly
        :hint="$t('oauth.application.client_secret_hint')"
        persistent-hint
        :class="{ 'd-none': !isCreate }"
      />
    </template>

    <template #clientType="{ item }">
      {{ lookupChoiceText(clientTypeChoices, item.clientType) }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #clientType.field="{ attrs, on }">
      <v-autocomplete
        v-bind="attrs"
        v-on="on"
        :items="clientTypeChoices"
        required
        :rules="$rules().required.build()"
      />
    </template>

    <template #algorithm="{ item }">
      {{ lookupChoiceText(algorithmChoices, item.algorithm) }}
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #algorithm.field="{ attrs, on }">
      <v-autocomplete
        v-bind="attrs"
        v-on="on"
        :items="algorithmChoices"
        required
        :rules="$rules().required.build()"
      />
    </template>

    <template #allowedScopes="{ item }">
      <v-chip v-for="scope in item.allowedScopes" :key="scope">
        {{
          lookupChoiceText(oauthScopes, scope, "name", "description")
        }} </v-chip
      >&nbsp;
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #allowedScopes.field="{ attrs, on }">
      <v-autocomplete
        v-bind="attrs"
        v-on="on"
        hide-no-data
        multiple
        filled
        :items="oauthScopes"
        item-text="description"
        item-value="name"
      />
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #redirectUris.field="{ attrs, on }">
      <v-text-field
        v-bind="attrs"
        v-on="on"
        filled
        :hint="$t('oauth.application.redirect_uris_hint')"
        persistent-hint
      />
    </template>

    <template #skipAuthorization="{ item }">
      <v-switch
        :input-value="item.skipAuthorization"
        disabled
        inset
        :false-value="false"
        :true-value="true"
      />
    </template>
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #skipAuthorization.field="{ attrs, on }">
      <v-switch
        v-bind="attrs"
        v-on="on"
        inset
        :false-value="false"
        :true-value="true"
      />
    </template>

    <template #icon="{ item }">
      <v-img
        v-if="item.icon.url"
        :src="item.icon.url"
        :alt="$t('oauth.application.icon')"
        max-width="6em"
      />
      <span v-else>–</span>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #icon.field="{ attrs, on }">
      <div aria-required="false">
        <file-field v-bind="attrs" v-on="on" accept="image/jpeg, image/png">
          <template #append-outer="{ fileUrl }">
            <v-img
              v-if="fileUrl"
              :src="fileUrl"
              :alt="$t('oauth.application.icon')"
              max-width="4em"
            />
          </template>
        </file-field>
      </div>
    </template>
  </c-r-u-d-list>
</template>

<script>
import {
  oauthApplications,
  initOauthApplication,
  createOauthApplications,
  patchOauthApplications,
  deleteOauthApplications,
  gqlOauthScopes,
} from "./oauthApplications.graphql";

import formRulesMixin from "../../mixins/formRulesMixin";

export default {
  name: "OAuthApplications",
  mixins: [formRulesMixin],
  data() {
    return {
      headers: [
        {
          text: this.$t("oauth.application.name"),
          value: "name",
          cols: 12,
        },
        {
          text: this.$t("oauth.application.icon"),
          value: "icon",
          cols: 12,
        },
        {
          text: this.$t("oauth.application.client_id"),
          value: "clientId",
          cols: 12,
          hidden: true,
        },
        {
          text: this.$t("oauth.application.client_secret"),
          value: "clientSecret",
          cols: 12,
          hidden: true,
        },
        {
          text: this.$t("oauth.application.client_type"),
          value: "clientType",
          cols: 12,
        },
        // Not in orig show, but in orig create
        {
          text: this.$t("oauth.application.algorithm"),
          value: "algorithm",
          cols: 12,
        },
        {
          text: this.$t("oauth.application.allowed_scopes"),
          value: "allowedScopes",
          cols: 12,
        },
        {
          text: this.$t("oauth.application.redirect_uris"),
          value: "redirectUris",
          cols: 12,
        },
        {
          text: this.$t("oauth.application.skip_authorization"),
          value: "skipAuthorization",
          cols: 12,
        },
      ],
      i18nKey: "oauth.application",
      gqlQuery: oauthApplications,
      gqlCreateMutation: createOauthApplications,
      gqlPatchMutation: patchOauthApplications,
      gqlDeleteMutation: deleteOauthApplications,
      clientTypeChoices: [
        {
          text: this.$t("oauth.application.client_type_confidential"),
          value: "CONFIDENTIAL",
        },
        {
          text: this.$t("oauth.application.client_type_public"),
          value: "PUBLIC",
        },
      ],
      algorithmChoices: [
        {
          text: this.$t("oauth.application.algorithm_no_oidc"),
          value: "A_",
        },
        {
          text: this.$t("oauth.application.algorithm_rsa"),
          value: "RS256",
        },
        {
          text: this.$t("oauth.application.algorithm_hmac"),
          value: "HS256",
        },
      ],
    };
  },
  computed: {
    defaultItem() {
      return {
        name: "",
        icon: null,
        clientId: this.initOauthApplication?.clientId,
        clientSecret: this.initOauthApplication?.clientSecret,
        clientType: "",
        algorithm: "A_",
        allowedScopes: "",
        redirectUris: "",
        skipAuthorization: false,
      };
    },
  },
  apollo: {
    initOauthApplication: {
      query: initOauthApplication,
      skip: true,
    },
    oauthScopes: {
      query: gqlOauthScopes,
    },
  },
  methods: {
    handleSave() {
      this.$apollo.queries.initOauthApplication.skip = true;
      this.queries.initOauthApplication.refetch();
    },
    lookupChoiceText(choices, value, valueKey = "value", textKey = "text") {
      return (choices.find((choice) => choice[valueKey] === value) || {
        [textKey]: value,
      })[textKey];
    },
  },
};
</script>

<style scoped>
.client_secret {
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 20em;
}
</style>
