<template>
  <v-autocomplete
    v-bind="$attrs"
    v-on="$listeners"
    hide-no-data
    :items="items"
    :item-text="getItemText"
    item-value="id"
    :loading="loading"
    :search-input.sync="searchString"
    :placeholder="serverSearch ? $t('actions.type_to_search') : ''"
  />
</template>

<script>
import queryMixin from "../../../mixins/queryMixin.js";
import { formPersons } from "./person.graphql";

export default {
  name: "PersonField",
  extends: "v-autocomplete",
  mixins: [queryMixin],
  props: {
    /**
     * The graphQL query used to retrieve the persons.
     */
    gqlQuery: {
      type: Object,
      required: false,
      default: () => formPersons,
    },
    serverSearch: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      searchString: "",
    };
  },
  methods: {
    getItemText(person) {
      if (person?.shortName) {
        return `${person.fullName} (${person.shortName})`;
      }
      return person.fullName;
    },
  },
  watch: {
    searchString: {
      handler(newValue) {
        if (this.serverSearch && this.$apollo.queries.items) {
          if (newValue) {
            this.additionalFilters = {
              name: newValue,
            };
            this.$apollo.queries.items.start();
          } else {
            this.items = [];
            this.$apollo.queries.items.stop();
          }
        }
      },
      immediate: true,
    },
  },
};
</script>
