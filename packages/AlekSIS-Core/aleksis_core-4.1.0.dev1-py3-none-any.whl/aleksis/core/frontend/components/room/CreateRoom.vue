<script setup>
import DialogObjectForm from "../generic/dialogs/DialogObjectForm.vue";
</script>

<template>
  <dialog-object-form v-bind="$props" v-on="$listeners">
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #name.field="{ attrs, on, item, setter }">
      <div aria-required="true">
        <v-text-field
          v-bind="attrs"
          v-on="on"
          :rules="rules.name"
          @input="handleNameInput($event, item, setter)"
        />
      </div>
    </template>

    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #shortName.field="{ attrs, on }">
      <div aria-required="true">
        <v-text-field v-bind="attrs" v-on="on" :rules="rules.shortName" />
      </div>
    </template>
  </dialog-object-form>
</template>

<script>
export default {
  name: "CreateRoom",
  extends: DialogObjectForm,
  props: {
    gqlQuery: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      rules: {
        name: [
          (name) =>
            (name && name.length > 0) || this.$t("cursus.errors.name_required"),
        ],
        shortName: [
          (name) =>
            (name && name.length > 0) ||
            this.$t("cursus.errors.short_name_required"),
        ],
      },
    };
  },
  methods: {
    handleNameInput(input, itemModel, setter) {
      if (!itemModel.shortName || itemModel.shortName.length < 2) {
        setter("shortName", input.substring(0, 3));
      }
    },
  },
};
</script>
