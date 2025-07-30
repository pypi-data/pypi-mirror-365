<template>
  <v-tooltip left>
    <template #activator="{ on, attrs }">
      <primary-action-button
        v-bind="{ ...$props, ...$attrs, ...attrs }"
        v-on="{ ...$listeners, ...on }"
        style="z-index: 5"
        fab
        large
        bottom
        fixed
        right
      >
        <v-icon>{{ iconText }}</v-icon>
      </primary-action-button>
    </template>
    <span>{{ $t(i18nKey) }}</span>
  </v-tooltip>
</template>

<script>
import PrimaryActionButton from "./PrimaryActionButton.vue";

export default {
  name: "FabButton",
  extends: PrimaryActionButton,
  components: { PrimaryActionButton },
  props: {
    iconText: {
      type: String,
      required: true,
    },
  },
};
</script>
