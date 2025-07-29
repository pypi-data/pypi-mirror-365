<script>
import permissionsMixin from "../../mixins/permissions";
import SecondaryActionButton from "../generic/buttons/SecondaryActionButton.vue";
import { buildQuery } from "./dashboardQuery";
import WidgetWrapper from "./WidgetWrapper.vue";
import { collections } from "aleksisAppImporter";

export default {
  name: "Dashboard",
  components: { SecondaryActionButton, WidgetWrapper },
  mixins: [permissionsMixin],
  mounted() {
    this.addPermissions(["core.edit_dashboard_rule"]);
  },
  data() {
    return {
      dashboardWidgets: [],
      isDefaultDashboard: false,
    };
  },
  computed: {
    canEdit() {
      return this.checkPermission("core.edit_dashboard_rule");
    },
    widgetInfoMap() {
      return collections.coreDashboardWidgets.items.reduce((map, widget) => {
        map[widget.typename] = widget;
        return map;
      }, {});
    },
  },
  apollo: {
    dashboardWidgets: {
      query: buildQuery,
      update: (data) => data.dashboard.my,
      result({ data }) {
        this.isDefaultDashboard = !data.dashboard.hasOwn;
      },
    },
  },
};
</script>

<template>
  <v-sheet>
    <div v-if="canEdit" class="d-flex justify-end mb-2">
      <secondary-action-button
        i18n-key="dashboard.edit"
        icon-text="$edit"
        :to="{ name: 'dashboard', query: { _ui_action: 'edit' } }"
      />
    </div>

    <div :class="{ dashboard: true, 'd-grid': !$vuetify.breakpoint.mobile }">
      <WidgetWrapper
        v-for="instance in dashboardWidgets"
        :key="instance.id"
        v-bind="instance"
      >
        <component
          :is="widgetInfoMap[instance.widget.__typename].component"
          v-bind="instance"
          class="widget"
        />
      </WidgetWrapper>
    </div>

    <v-subheader
      v-if="canEdit && isDefaultDashboard"
      class="justify-end px-0 pt-1 auto-height"
    >
      {{ $t("dashboard.customizing_notice") }}
    </v-subheader>
  </v-sheet>
</template>

<style scoped>
.auto-height {
  height: auto;
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1em;
}

.d-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-auto-rows: 1fr;
}

.widget {
  width: 100%;
  height: 100%;
}
</style>
