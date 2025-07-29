/*
 * Configuration for Vuetify
 */

import "@/@mdi/font/css/materialdesignicons.css";
import "@/vuetify/dist/vuetify.min.css";
import "../css/global.scss";

const vuetifyOpts = {
  icons: {
    iconfont: "mdi", // default - only for display purposes
    values: {
      cancel: "mdi-close",
      delete: "mdi-close", // Not a trashcan due to vuetify using this icon inside chips for closing etc.
      deleteContent: "mdi-delete-outline",
      success: "mdi-check",
      info: "mdi-information-outline",
      warning: "mdi-alert-outline",
      error: "mdi-alert-octagon-outline",
      prev: "mdi-chevron-left",
      next: "mdi-chevron-right",
      checkboxOn: "mdi-checkbox-marked-outline",
      checkboxIndeterminate: "mdi-minus-box-outline",
      edit: "mdi-pencil-outline",
      preferences: "mdi-cog-outline",
      save: "mdi-content-save-outline",
      search: "mdi-magnify",
      filterEmpty: "mdi-filter-outline",
      filterSet: "mdi-filter",
      send: "mdi-send-outline",
      holidays: "mdi-calendar-weekend-outline",
      home: "mdi-home-outline",
      groupType: "mdi-shape-outline",
      role: "mdi-badge-account-horizontal-outline",
      print: "mdi-printer-outline",
      schoolTerm: "mdi-calendar-range-outline",
      updatePwa: "mdi-update",
      dashboardWidgetOff: "mdi-dots-horizontal-circle-outline",
      dashboardWidgetReady: "mdi-circle-off-outline",
      dashboardWidgetBroken: "mdi-alert-circle-outline",
      dashboardWidgetOn: "mdi-check-circle-outline",
    },
  },
  theme: {
    options: {
      customProperties: true,
    },
  },
};

export default vuetifyOpts;
