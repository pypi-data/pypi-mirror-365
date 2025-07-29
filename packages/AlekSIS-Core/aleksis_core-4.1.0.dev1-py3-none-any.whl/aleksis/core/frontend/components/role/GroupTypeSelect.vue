<script>
import { roles } from "./role.graphql";
export default {
  name: "RoleSelect",
  apollo: {
    items: {
      query: roles,
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
    prepend-inner-icon="$role"
    :items="items"
    item-text="name"
    item-value="id"
    :loading="$apollo.queries.items.loading"
    :label="$t('role.title')"
  />
</template>
