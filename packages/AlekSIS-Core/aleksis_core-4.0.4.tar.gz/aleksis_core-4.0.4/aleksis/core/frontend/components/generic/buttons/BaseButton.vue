<template>
  <v-tooltip bottom :disabled="!icon && !forceTooltip" eager tag="div">
    <template #activator="{ on, attrs }">
      <v-btn
        v-bind="{ ...$props, ...attrs, ...$attrs }"
        v-on="{ ...on, ...$listeners }"
        :aria-label="$t(i18nKey)"
      >
        <slot>
          <v-icon v-if="iconText" :left="!icon">{{ iconText }}</v-icon>
          <span v-if="!icon" v-t="i18nKey" />
        </slot>
      </v-btn>
    </template>
    <span v-if="forceTooltip || icon" v-t="i18nKey" />
  </v-tooltip>
</template>

<script>
import VBtn from "@/vuetify/lib/components/VBtn";

export default {
  name: "BaseButton",
  inheritAttrs: true,
  extends: VBtn,
  props: {
    i18nKey: {
      type: String,
      required: true,
    },
    iconText: {
      type: String,
      required: false,
      default: undefined,
    },
    /**
     * Iconify the button.
     * Rund button that shows only the icon.
     */
    icon: {
      type: Boolean,
      required: false,
      default: false,
    },
    forceTooltip: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
};
</script>

<style scoped></style>
