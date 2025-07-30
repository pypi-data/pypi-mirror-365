<template>
  <v-data-table
    v-bind="$attrs"
    v-on="$listeners"
    :headers="tableHeaders"
    :items="items"
    :items-per-page="itemsPerPage"
    :footer-props="footerProps"
    :loading="loading"
    :class="elevated ? 'elevation-2' : ''"
    :search="search"
    :custom-filter="deepSearch"
    :sort-by.sync="sortBy"
    :sort-desc.sync="sortDesc"
    multi-sort
    @update:sort-by="handleSortChange"
    @update:sort-desc="handleSortChange"
    :show-select="showSelect"
    selectable-key="selectable"
    @item-selected="handleItemSelected"
    @toggle-select-all="handleToggleAll"
    @current-items="checkSelectAll"
    :show-expand="showExpand"
  >
    <!-- Bar template -->
    <template #top>
      <c-r-u-d-bar
        v-bind="$attrs"
        v-on="$listeners"
        ref="bar"
        :gql-order-by="orderBy"
        @mode="handleMode"
        @create="$emit('create')"
        @save="$emit('save', $event)"
        @loading="handleLoading"
        @rawItems="$emit('rawItems', $event)"
        @items="handleItems"
        @lastQuery="$emit('lastQuery', $event)"
        @search="search = $event"
        @selectable="selectable = true"
        :selection="showSelect ? selection : []"
        @selection="selection = $event"
        @deletable="showDelete = true"
        minimal-patch
      >
        <template #title="{ attrs, on }">
          <slot name="title" :attrs="attrs" :on="on" />
        </template>

        <template #filters="{ attrs, on }">
          <slot name="filters" :attrs="attrs" :on="on" />
        </template>

        <template
          v-for="header in $attrs.headers.filter(
            (header) => !header.disableEdit,
          )"
          #[fieldSlot(header)]="{ item, isCreate, on, attrs }"
        >
          <slot
            :name="fieldSlot(header)"
            :attrs="attrs"
            :on="on"
            :item="item"
            :is-create="isCreate"
          />
        </template>
        <template #additionalActions="{ attrs, on }">
          <slot name="additionalActions" :attrs="attrs" :on="on" />
        </template>
        <template #createComponent="createComponentProps">
          <slot name="createComponent" v-bind="createComponentProps" />
        </template>
      </c-r-u-d-bar>
    </template>

    <!-- Header slot template -->
    <template
      v-for="(_header, idx) in $attrs.headers"
      #[headerSlot(_header)]="{ header }"
    >
      <slot :name="header.value + '.header'" :header="header">
        {{ header.text }}
      </slot>
    </template>

    <!-- Row template -->
    <template
      v-for="(header, idx) in $attrs.headers"
      #[rowSlot(header)]="{ item }"
    >
      <slot :name="header.value" :item="item">
        {{ getKeysRecursive(header.value, item) }}
      </slot>
    </template>

    <!-- Add a action (= btn) column -->
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.actions="{ item }">
      <!-- @slot Add additional action to action column -->
      <slot name="actions" :item="item" />
      <edit-button
        v-if="$attrs['enable-edit'] && 'canEdit' in item && item.canEdit"
        icon
        color="secondary"
        @click="$refs.bar.handleEdit(item)"
        :disabled="mode || loading || $attrs.lock"
      />
      <delete-button
        v-if="showDelete && 'canDelete' in item && item.canDelete"
        icon
        color="error"
        @click="$refs.bar.handleDelete(item)"
        :disabled="mode || loading || $attrs.lock"
      />
    </template>

    <!-- Customize expanded rows -->
    <template #expanded-item="{ headers, item }">
      <td :colspan="headers.length">
        <slot name="expanded-item" :item="item" />
      </td>
    </template>

    <template #footer>
      <slot name="footer"></slot>
    </template>
    <template #loading>
      <slot name="loading"></slot>
    </template>
    <template #no-data>
      <slot name="no-data">
        <div class="d-flex flex-column align-center justify-center">
          <mascot type="ready_for_items" width="33%" min-width="250px" />
          <div class="mb-2">
            {{ $t("$vuetify.noDataText") }}
          </div>
        </div>
      </slot>
    </template>
    <template #no-results>
      <slot name="no-results">
        <div class="d-flex flex-column align-center justify-center">
          <mascot type="searching" width="33%" min-width="250px" />
          <div class="mb-2">
            {{ $t("$vuetify.dataIterator.noResultsText") }}
          </div>
        </div>
      </slot>
    </template>
  </v-data-table>
</template>

<script>
import CRUDBar from "./CRUDBar.vue";
import EditButton from "./buttons/EditButton.vue";
import DeleteButton from "./buttons/DeleteButton.vue";
import Mascot from "./mascot/Mascot.vue";

import deepSearchMixin from "../../mixins/deepSearchMixin";
import loadingMixin from "../../mixins/loadingMixin.js";
import syncSortMixin from "../../mixins/syncSortMixin.js";
import itemsPerPageMixin from "../../mixins/itemsPerPageMixin.js";

export default {
  name: "CRUDList",
  components: {
    CRUDBar,
    EditButton,
    DeleteButton,
    Mascot,
  },
  mixins: [deepSearchMixin, loadingMixin, syncSortMixin, itemsPerPageMixin],
  props: {
    /**
     * Elevate the table?
     * @values true, false
     */
    elevated: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Show the select checkboxes if the table contains selectable items
     * @values true, false
     */
    showSelect: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Show the action column
     * @values true, false
     */
    showActionColumn: {
      type: Boolean,
      required: false,
      default: true,
    },
    /**
     * Show the expand toggle?
     * @values true, false
     */
    showExpand: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  emits: ["lastQuery", "mode", "rawItems", "items"],
  data() {
    return {
      // Items shown in List = items with added selectable key
      items: [],
      // Search
      search: "",
      // Item selection
      selectable: false,
      selection: [],
      allSelected: false,
      // Delete
      showDelete: false,
      // Modal state
      mode: false,
    };
  },
  computed: {
    // Compute actual tableHeaders from headers by maybe adding a
    // delete column & filtering out hidden colums.
    tableHeaders() {
      return this.$attrs.headers
        .concat(
          this.showActionColumn &&
            (this.showDelete || this.$attrs["enable-edit"])
            ? [
                {
                  text: this.$t("actions.title"),
                  value: "actions",
                  sortable: false,
                  align: "right",
                },
              ]
            : [],
        )
        .filter((header) => !header.hidden);
    },
  },
  methods: {
    handleMode(mode) {
      this.mode = mode;
      // Pass on; documented in CRUDBar.
      this.$emit("mode", mode);
    },
    handleItems(items) {
      this.items = items;
      // Pass on; documented in queryMixin.
      this.$emit("items", items);
    },
    // Item selection
    handleItemSelected({ item, value }) {
      if (value) {
        this.selection.push(item);
      } else {
        const index = this.selection.indexOf(item);
        if (index >= 0) {
          this.selection.splice(index, 1);
        }
      }
    },
    handleToggleAll({ items, value }) {
      if (value) {
        // There is a bug in vuetify: items contains all elements, even those that aren't selectable
        this.selection = items.filter((item) => item.selectable);
      } else {
        this.selection = [];
      }
      this.allSelected = value;
    },
    checkSelectAll(newItems) {
      // TODO: Should this handle deletion of items?
      // = still on selection but not in items anymore
      if (this.allSelected) {
        this.handleToggleAll({
          items: newItems,
          value: true,
        });
      }
    },
    // Template names
    fieldSlot(header) {
      return header.value + ".field";
    },
    rowSlot(header) {
      return "item." + header.value;
    },
    headerSlot(header) {
      return "header." + header.value;
    },
  },
};
</script>
