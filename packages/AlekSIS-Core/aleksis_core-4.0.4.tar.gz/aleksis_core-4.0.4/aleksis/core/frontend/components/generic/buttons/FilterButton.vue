<template>
  <secondary-action-button
    v-bind="$attrs"
    v-on="$listeners"
    :i18n-key="i18nKey"
  >
    <v-icon v-if="filterIcon" left>{{ filterIcon }}</v-icon>
    <v-badge color="secondary" :value="numFilters" :content="numFilters" inline>
      <span v-t="i18nKey" />
    </v-badge>
    <icon-button
      @click.stop="$emit('clear')"
      small
      v-if="numFilters"
      class="mr-n1"
      icon-text="$clear"
      i18n-key="actions.clear_filters"
    />
  </secondary-action-button>
</template>

<script>
import SecondaryActionButton from "./SecondaryActionButton.vue";
import IconButton from "./IconButton.vue";

export default {
  name: "FilterButton",
  components: { IconButton, SecondaryActionButton },
  extends: SecondaryActionButton,
  computed: {
    filterIcon() {
      return this.hasFilters || this.numFilters > 0
        ? "$filterSet"
        : "$filterEmpty";
    },
  },
  props: {
    i18nKey: {
      type: String,
      required: false,
      default: "actions.filter",
    },
    hasFilters: {
      type: Boolean,
      required: false,
      default: false,
    },
    numFilters: {
      type: Number,
      required: false,
      default: 0,
    },
  },
};
</script>
