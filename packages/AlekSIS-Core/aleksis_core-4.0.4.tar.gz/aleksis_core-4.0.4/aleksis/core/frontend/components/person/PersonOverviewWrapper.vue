<template>
  <component :is="currentComponent" v-bind="componentProps" />
</template>

<script>
import PersonForm from "./PersonForm.vue";
import PersonOverview from "./PersonOverview.vue";

export default {
  computed: {
    currentComponent() {
      return this.$route.query._ui_action === "edit"
        ? PersonForm
        : PersonOverview;
    },
    componentProps() {
      return this.$route.query._ui_action === "edit"
        ? {
            fallbackUrl: { name: "core.personById", params: { id: this.id } },
            isCreate: false,
            id: this.id,
          }
        : {
            id: this.id,
          };
    },
  },
  props: {
    id: {
      type: String,
      required: false,
      default: null,
    },
  },
};
</script>
