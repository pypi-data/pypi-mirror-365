<script>
import mutateMixin from "../../../mixins/mutateMixin";
import { buildCreateMutation } from "./dashboardWidgetQuerying";
import { widgetTypes } from "./availableWidgets.graphql";
import ButtonMenu from "../../generic/ButtonMenu.vue";

export default {
  name: "CreateDashboardWidget",
  components: { ButtonMenu },
  mixins: [mutateMixin],
  props: {
    widgetInfoMap: {
      type: Object,
      default: () => ({}),
      required: false,
    },
  },
  data() {
    return {
      widgetTypes: [],
    };
  },
  methods: {
    create(type) {
      this.mutate(
        buildCreateMutation(),
        {
          widgetTypes: [type],
        },
        (cached, incoming) => {
          return [...incoming, ...cached];
        },
      );
    },
  },
  apollo: {
    widgetTypes: {
      query: widgetTypes,
      update: (data) => data.dashboard.widgetTypes,
    },
  },
};
</script>

<template>
  <button-menu
    text-translation-key="actions.create_widget"
    icon="$plus"
    :outlined="false"
    :text="false"
    color="primary"
  >
    <v-list-item
      v-for="type in widgetTypes"
      :key="type.typeName"
      @click="create(type.modelName)"
    >
      <v-list-item-title
        v-t="widgetInfoMap[type.typeName]?.nameKey || type.modelName"
      />
    </v-list-item>
  </button-menu>
</template>
