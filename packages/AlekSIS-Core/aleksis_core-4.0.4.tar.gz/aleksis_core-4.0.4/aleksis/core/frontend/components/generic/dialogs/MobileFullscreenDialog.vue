<template>
  <v-dialog
    v-bind="$attrs"
    v-on="$listeners"
    :fullscreen="$vuetify.breakpoint.xs"
    :hide-overlay="$vuetify.breakpoint.xs"
    :max-width="maxWidth"
  >
    <template #activator="activator">
      <slot name="activator" v-bind="activator"></slot>
    </template>
    <template #default>
      <slot>
        <v-card class="d-flex flex-column">
          <v-card-title>
            <slot name="title"></slot>
            <v-spacer v-if="closeButton" />
            <dialog-close-button v-if="closeButton" @click="close" />
          </v-card-title>
          <v-card-text>
            <slot name="content"></slot>
          </v-card-text>
          <v-spacer />
          <v-divider />
          <v-card-actions>
            <slot name="actionsLeft"></slot>
            <v-spacer></v-spacer>
            <slot name="actions"></slot>
          </v-card-actions>
        </v-card>
      </slot>
    </template>
  </v-dialog>
</template>

<script>
import DialogCloseButton from "../buttons/DialogCloseButton.vue";

export default {
  name: "MobileFullscreenDialog",
  components: { DialogCloseButton },
  extends: "v-dialog",
  props: {
    maxWidth: {
      type: [String, Number],
      required: false,
      default: "600px",
    },
    closeButton: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
  methods: {
    close() {
      this.$emit("input", false);
    },
  },
};
</script>

<style scoped></style>
