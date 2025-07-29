<template>
  <v-menu
    transition="slide-y-transition"
    offset-y
    :close-on-content-click="closeOnContentClick"
  >
    <template #activator="menu">
      <slot name="activator" v-bind="menu">
        <v-tooltip bottom :disabled="!iconOnly">
          <template #activator="tooltip">
            <v-btn
              :outlined="outlined"
              :text="text"
              :icon="!outlined && iconOnly"
              v-bind="{ ...tooltip.attrs, ...menu.attrs, ...$attrs }"
              v-on="{ ...tooltip.on, ...menu.on }"
              :aria-label="$t(textTranslationKey)"
            >
              <v-icon :left="!iconOnly" :center="iconOnly">
                {{ icon }}
              </v-icon>
              <span v-if="!iconOnly">{{ $t(textTranslationKey) }}</span>
            </v-btn>
          </template>
          <span v-if="iconOnly">{{ $t(textTranslationKey) }}</span>
        </v-tooltip>
      </slot>
    </template>

    <v-list>
      <slot />
    </v-list>
  </v-menu>
</template>

<script>
export default {
  name: "ButtonMenu",
  props: {
    icon: {
      type: String,
      required: false,
      default: "mdi-dots-horizontal",
    },
    textTranslationKey: {
      type: String,
      required: true,
    },
    iconOnly: {
      type: Boolean,
      required: false,
      default: false,
    },
    closeOnContentClick: {
      type: Boolean,
      required: false,
      default: true,
    },
    outlined: {
      type: Boolean,
      default: true,
    },
    text: {
      type: Boolean,
      default: true,
    },
  },
};
</script>

<style scoped></style>
