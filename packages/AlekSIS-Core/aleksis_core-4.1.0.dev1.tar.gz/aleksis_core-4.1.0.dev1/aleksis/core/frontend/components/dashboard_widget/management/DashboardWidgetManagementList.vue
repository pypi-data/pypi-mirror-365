<script setup>
import CRUDIterator from "../../generic/CRUDIterator.vue";
import DashboardWidgetWrapper from "../ManageDashboardWidgetWrapper.vue";
import CreateDashboardWidget from "./CreateDashboardWidget.vue";
</script>

<template>
  <c-r-u-d-iterator
    i18n-key="alsijil.coursebook.statistics"
    :gql-query="gqlQuery"
    :gql-data-key="gqlDataKey"
    :enable-create="false"
    :enable-edit="false"
    :elevated="false"
    @lastQuery="lastQuery = $event"
  >
    <template #additionalActions>
      <create-dashboard-widget
        :affected-query="lastQuery"
        gql-data-key="dashboard.widgets"
        :widget-info-map="widgetInfoMap"
      />
      <secondary-action-button
        icon-text="mdi-view-dashboard-edit-outline"
        i18n-key="dashboard.manage_default_dashboard"
        :to="{ name: 'core.editDefaultDashboard' }"
      />
    </template>
    <template #default="{ items }">
      <dashboard-widget-wrapper
        v-for="item in items"
        :key="item.id"
        :widget-data="item"
        :widget-info="widgetInfoMap[item.__typename]"
        class="mb-2"
        :affected-query="lastQuery"
        gql-data-key="dashboard.widgets"
      />
    </template>
  </c-r-u-d-iterator>
</template>

<script>
import { buildQuery } from "./dashboardWidgetQuerying";
import { collections } from "aleksisAppImporter";

export default {
  name: "DashboardWidgetManagementList",
  data() {
    return {
      headers: [
        {
          text: this.$t("dashboard_widget.name"),
          value: "title",
        },
        {
          text: this.$t("dashboard_widget.status"),
          value: "status",
        },
      ],
      selected: [],
      i18nKey: "dashboard_widget",
      gqlQuery: buildQuery(),
      gqlDataKey: "dashboard.widgets",
      gqlCreateMutation: {},
      gqlPatchMutation: {},
      gqlDeleteMutation: {},
      defaultItem: {
        title: "",
        status: "OFF",
      },
      lastQuery: null,
    };
  },
  computed: {
    widgetInfoMap() {
      return collections.coreDashboardWidgets.items.reduce((map, widget) => {
        map[widget.typename] = widget;
        return map;
      }, {});
    },
  },
};
</script>
