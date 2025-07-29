import loadingMixin from "./loadingMixin.js";

/**
 * This mixin provides generic item query via graphQL.
 * The query result is available in items.
 */
export default {
  mixins: [loadingMixin],
  props: {
    /**
     * The graphQL query
     */
    gqlQuery: {
      type: [Function, Object],
      required: true,
    },
    /**
     * Optional arguments to graphQL query
     */
    // UPDATE NOTICE: Name change from additionalQueryArgs (prop was so far not used anyway)
    gqlAdditionalQueryArgs: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * OrderBy directive used in the graphQL query
     */
    gqlOrderBy: {
      type: Array,
      required: false,
      default: () => [],
    },
    /**
     * Filter object used in the graphQL query
     */
    gqlFilters: {
      type: Object,
      required: false,
      default: () => ({}),
    },
    /**
     * Transform function for the data returned by the query
     */
    getGqlData: {
      type: Function,
      required: false,
      default: (item) => item,
    },
    /**
     * Key of the desired data payload
     * Key can be a single key or nested keys seperated by a '.'
     */
    gqlDataKey: {
      type: String,
      required: false,
      default: "items",
    },
    /**
     * Key of the apollo query
     * Key can be a single key or nested keys seperated by a '.'
     */
    gqlQueryKey: {
      type: String,
      required: false,
      default: "items",
    },
  },
  emits: ["rawItems", "items", "lastQuery"],
  data() {
    return {
      internalAdditionalFilters: {},
      filterString: "{}",
      lastQuery: {},
      internalSkip: false,
      items: [],
    };
  },
  computed: {
    additionalFilters: {
      get() {
        return this.internalAdditionalFilters;
      },
      set(filters) {
        this.internalAdditionalFilters = filters;
        this.updateFilterString();
      },
    },
    skip() {
      return this.internalSkip;
    },
  },
  watch: {
    gqlFilters: {
      handler() {
        this.updateFilterString();
      },
      deep: true,
    },
  },
  methods: {
    handleItems(items) {
      return items;
    },
    updateFilterString() {
      this.filterString = JSON.stringify({
        ...this.gqlFilters,
        ...this.internalAdditionalFilters,
      });
    },
  },
  apollo: {
    items() {
      return {
        query: this.gqlQuery,
        variables() {
          const orderBy = this.gqlOrderBy.length
            ? { orderBy: this.gqlOrderBy }
            : {};
          const filters = {
            filters: this.filterString,
          };
          return {
            ...this.gqlAdditionalQueryArgs,
            ...orderBy,
            ...filters,
          };
        },
        watchLoading(loading) {
          this.handleLoading(loading);
        },
        update: (data) => {
          this.lastQuery = this.getKeysRecursive(
            this.gqlQueryKey,
            this.$apollo.queries,
          );
          /**
           * Emits the last query
           * Use this to update the cache
           *
           * @property {Object} graphQL query
           */
          this.$emit("lastQuery", this.lastQuery);

          const rawItems = this.getKeysRecursive(this.gqlDataKey, data);
          /**
           * Emits the raw updated items
           * before processing with getGqlData
           *
           * @property {array} Raw query result
           */
          this.$emit("rawItems", rawItems);

          const items = this.handleItems(this.getGqlData(rawItems));
          /**
           * Emits updated items
           * either from a graphQL query
           * or if the cached result was updated.
           *
           * @property {array} Query restult
           */
          this.$emit("items", items);
          return items;
        },
        skip() {
          return this.skip;
        },
      };
    },
  },
};
