<script>
import { groupTypes } from "./groupType.graphql";
export default {
  name: "GroupTypeSelect",
  apollo: {
    items: {
      query: groupTypes,
    },
  },
  data() {
    return {
      items: [],
    };
  },
};
</script>

<template>
  <v-autocomplete
    v-bind="$attrs"
    v-on="$listeners"
    clearable
    prepend-inner-icon="$groupType"
    :items="items"
    item-text="name"
    item-value="id"
    :loading="$apollo.queries.items.loading"
    :label="$t('group.group_type.title')"
  />
</template>
