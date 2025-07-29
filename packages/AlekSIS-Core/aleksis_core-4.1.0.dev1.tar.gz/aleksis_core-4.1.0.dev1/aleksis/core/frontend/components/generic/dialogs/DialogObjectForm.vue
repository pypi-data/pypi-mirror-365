<template>
  <mobile-fullscreen-dialog
    v-model="dialogMode"
    max-width="555px"
    :close-button="false"
  >
    <template #activator="{ on, attrs }">
      <!-- @slot Insert component that activates the dialog-object-form -->
      <slot name="activator" v-bind="{ on, attrs }" />
    </template>

    <template #title>
      <!-- @slot The title of the dialog-object-form -->
      <slot name="title">
        <span class="text-h5">
          {{ $refs?.form?.title }}
        </span>
      </slot>
    </template>

    <template #content>
      <object-form
        ref="form"
        v-bind="objectFormProps"
        v-on="$listeners"
        :valid.sync="valid"
        @loading="handleLoading"
        @save="handleSave"
        @cancel="dialogMode = false"
      >
        <template v-for="(_, slot) of $scopedSlots" #[slot]="scope"
          ><slot :name="slot" v-bind="scope"
        /></template>
      </object-form>
    </template>

    <template #actions>
      <cancel-button @click="dialogMode = false" :disabled="loading" />
      <save-button
        @click="$refs.form.submit()"
        :loading="loading"
        :disabled="!valid"
        class="ml-2"
      />
    </template>
  </mobile-fullscreen-dialog>
</template>

<script>
import SaveButton from "../buttons/SaveButton.vue";
import CancelButton from "../buttons/CancelButton.vue";
import MobileFullscreenDialog from "./MobileFullscreenDialog.vue";
import openableDialogMixin from "../../../mixins/openableDialogMixin";
import objectFormPropsMixin from "../../../mixins/objectFormPropsMixin";
import ObjectForm from "../crud/ObjectForm.vue";
import loadingMixin from "../../../mixins/loadingMixin";

/**
 * This component provides a form for creating or updating objects via graphQL (createOrPatchMixin)
 */
export default {
  name: "DialogObjectForm",
  components: {
    ObjectForm,
    CancelButton,
    SaveButton,
    MobileFullscreenDialog,
  },
  mixins: [openableDialogMixin, objectFormPropsMixin, loadingMixin],
  emits: ["cancel", "save"],
  methods: {
    handleSave(items) {
      this.dialogMode = false;
      this.$emit("save", items);
    },
  },
  data() {
    return {
      valid: false,
    };
  },
  mounted() {
    this.$on("cancel", this.close);
  },
};
</script>
