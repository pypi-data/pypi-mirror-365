<script>
import WidgetStatus from "./WidgetStatus.vue";
import ButtonMenu from "../generic/ButtonMenu.vue";
import MarkWidgetDialog from "./MarkWidgetDialog.vue";
import mutatePropsMixin from "../../mixins/mutatePropsMixin";
import WidgetTitleDialog from "./WidgetTitleDialog.vue";

export default {
  name: "DashboardWidgetWrapper",
  components: { WidgetTitleDialog, ButtonMenu, MarkWidgetDialog, WidgetStatus },
  mixins: [mutatePropsMixin],
  props: {
    mode: {
      type: String,
      default: "widget",
    },
    widgetData: {
      type: Object,
      required: true,
    },
    widgetInfo: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      loading: false,
    };
  },
};
</script>

<template>
  <v-card>
    <v-card-title>
      <div>
        <widget-title-dialog
          :widget="widgetData"
          v-bind="mutateProps"
          gql-data-key="dashboard.widgets"
        />
        <v-chip label outlined small>
          {{ $t(widgetInfo.shortNameKey) }}
        </v-chip>
      </div>
      <v-spacer />
      <widget-status :status="widgetData.status" :loading="loading" />
      <mark-widget-dialog
        :status="widgetData.status"
        :widget="widgetData"
        v-bind="mutateProps"
        gql-data-key="dashboard.widgets"
        @loading="loading = $event"
      />
    </v-card-title>
    <v-card-text>
      <component
        :is="widgetInfo.management"
        :widget="widgetData"
        v-bind="mutateProps"
      />
    </v-card-text>
  </v-card>
</template>
