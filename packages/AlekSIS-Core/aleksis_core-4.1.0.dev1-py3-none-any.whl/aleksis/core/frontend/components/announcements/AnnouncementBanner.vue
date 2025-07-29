<script>
import MobileFullscreenDialog from "../generic/dialogs/MobileFullscreenDialog.vue";
import BaseButton from "../generic/buttons/BaseButton.vue";
import DialogCloseButton from "../generic/buttons/DialogCloseButton.vue";

export default {
  name: "AnnouncementBanner",
  components: {
    DialogCloseButton,
    BaseButton,
    MobileFullscreenDialog,
  },
  props: {
    announcement: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      collapsed: true,
      dialogMode: false,
    };
  },
};
</script>

<template>
  <v-banner
    v-bind="$attrs"
    v-on="$listeners"
    color="warning white--text"
    icon="mdi-bullhorn-variant-outline"
    icon-color="white"
    id="banner"
  >
    <div class="d-flex align-center">
      <strong>{{ announcement.title }}</strong>
      <v-spacer />
      <base-button
        text
        color="white"
        i18n-key="actions.more"
        @click="dialogMode = true"
        class="float-right"
      />
    </div>

    <mobile-fullscreen-dialog
      v-model="dialogMode"
      hide-actions
      :close-button="false"
    >
      <template #title>
        <div class="d-flex align-center full-width">
          <v-icon color="primary" large class="mr-2">
            mdi-bullhorn-variant-outline
          </v-icon>
          {{ announcement.title }}
          <v-spacer />
          <dialog-close-button @click="dialogMode = false" class="ml-2" />
        </div>
      </template>
      <template #content>
        <p>{{ announcement.description }}</p>

        <small
          >{{
            $d($parseISODate(announcement.datetimeStart), "shortDateTime")
          }}–{{
            $d($parseISODate(announcement.datetimeEnd), "shortDateTime")
          }}</small
        >
      </template>
    </mobile-fullscreen-dialog>
  </v-banner>
</template>

<style>
#banner > .v-banner__wrapper {
  padding-block: 4px;
}
</style>
