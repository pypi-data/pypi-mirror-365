<template>
  <icon-button
    v-bind="{ ...$props, ...$attrs }"
    v-on="$listeners"
    :icon-text="iconText"
    :i18n-key="i18nKey"
    large
  />
</template>

<script>
import IconButton from "./IconButton.vue";

export default {
  name: "DialogCloseButton",
  components: { IconButton },
  inheritAttrs: true,
  extends: IconButton,
  props: {
    iconText: {
      required: false,
      default: "$close",
    },
    i18nKey: {
      required: false,
      default: "actions.close",
    },
  },
};
</script>
