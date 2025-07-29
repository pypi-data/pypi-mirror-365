<script>
import mutateMixin from "../../mixins/mutateMixin";
import { updateDashboardWidgets } from "./management/dashboardWidgetManagement.graphql";

export default {
  name: "WidgetTitleDialog",
  mixins: [mutateMixin],
  emits: ["update"],
  props: {
    widget: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      innerValue: "",
    };
  },
  mounted() {
    this.innerValue = this.widget.title;
  },
  methods: {
    cancel() {
      this.innerValue = this.widget.title;
    },
    save() {
      this.mutate(
        updateDashboardWidgets,
        {
          input: [
            {
              id: this.widget.id,
              title: this.innerValue,
            },
          ],
        },
        (cached, incoming) => {
          incoming.forEach((widget) => {
            const index = cached.findIndex((c) => c.id === widget.id);
            cached[index].status = widget.status;
            cached[index].title = widget.title;
          });
          return cached;
        },
      );
    },
  },
};
</script>

<template>
  <span class="db-widget-dialog">
    <v-edit-dialog
      :return-value.sync="innerValue"
      large
      persistent
      @cancel="cancel"
      @save="save"
    >
      <span class="mr-1">
        {{ widget.title }}
      </span>
      <template #input>
        <v-text-field
          v-model="innerValue"
          label="Edit"
          single-line
        ></v-text-field>
      </template>
    </v-edit-dialog>
  </span>
</template>

<style>
.db-widget-dialog .v-small-dialog__activator,
.db-widget-dialog .v-menu {
  display: inline;
}
</style>
