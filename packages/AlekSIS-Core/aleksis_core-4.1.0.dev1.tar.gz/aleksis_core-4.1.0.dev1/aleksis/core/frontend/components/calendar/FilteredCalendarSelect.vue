<script>
export default {
  name: "FilteredCalendarSelect",
  props: {
    value: {
      types: [Object, Array],
      required: false,
      default: null,
    },
    types: {
      type: Object,
      required: true,
    },
    items: {
      type: Array,
      required: true,
    },
    searchPlaceholderKey: {
      type: String,
      required: false,
      default: "actions.search",
    },
    multiple: {
      type: Boolean,
      required: false,
      default: false,
    },
    itemUID: {
      type: String,
      required: false,
      default: "uid",
    },
    itemType: {
      type: String,
      required: false,
      default: "type",
    },
  },
  data() {
    return {
      innerSelected: [],
      search: "",
      selectedTypes: [],
    };
  },
  watch: {
    innerSelected(val) {
      this.$emit("input", val);
    },
  },
  computed: {
    itemsFiltered() {
      // Filtered events by selected types
      return this.items.filter(
        (i) => this.selectedTypes.indexOf(i[this.itemType]) !== -1,
      );
    },
  },
  mounted() {
    this.selectedTypes = Object.keys(this.types);
  },
};
</script>

<template>
  <div>
    <v-card-text class="mb-0">
      <!-- Search field -->
      <v-text-field
        search
        filled
        rounded
        clearable
        autofocus
        v-model="search"
        :placeholder="$t(searchPlaceholderKey)"
        prepend-inner-icon="mdi-magnify"
        hide-details="auto"
        class="mb-2"
      />

      <!-- Filter by event types -->
      <v-btn-toggle v-model="selectedTypes" dense block multiple class="d-flex">
        <v-btn
          v-for="type in types"
          :key="type.id"
          class="flex-grow-1"
          :value="type.id"
        >
          {{ $t(type.nameKey) }}
        </v-btn>
      </v-btn-toggle>
    </v-card-text>

    <!-- Select groups of events -->
    <v-data-iterator
      :items="itemsFiltered"
      :item-key="itemUID"
      :search="search"
      single-expand
      disable-pagination
    >
      <template #default="{ items, isExpanded, expand }">
        <v-list class="scrollable-list">
          <v-list-item-group v-model="innerSelected" :multiple="multiple">
            <v-list-item
              v-for="item in items"
              :value="item"
              :key="item[itemUID]"
            >
              <template #default="{ active }">
                <v-list-item-icon color="primary">
                  <v-icon v-if="types[item[itemType]].icon" color="secondary">
                    {{ types[item[itemType]].icon }}
                  </v-icon>
                  <v-icon v-else color="secondary">mdi-grid</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{
                    item[types[item[itemType]].title]
                  }}</v-list-item-title>
                </v-list-item-content>
                <v-list-item-action v-if="multiple">
                  <v-checkbox :input-value="active" />
                </v-list-item-action>
              </template>
            </v-list-item>
          </v-list-item-group>
        </v-list>
      </template>
    </v-data-iterator>
  </div>
</template>

<style scoped>
.scrollable-list {
  height: 100%;
  overflow-y: scroll;
}
</style>
