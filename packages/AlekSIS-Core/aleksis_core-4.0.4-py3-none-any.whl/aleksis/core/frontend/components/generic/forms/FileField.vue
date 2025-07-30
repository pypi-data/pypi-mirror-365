<template>
  <v-file-input
    v-model="internalState"
    v-bind="$attrs"
    v-on="$listeners"
    :clearable="false"
    persistent-hint
    :hint="hint"
  >
    <template #append>
      <icon-button
        v-if="showClear"
        @click.stop="clearOrDelete"
        icon-text="$clear"
        i18n-key="actions.clear"
      />
    </template>
    <template #append-outer>
      <v-expand-x-transition>
        <div
          v-show="(!internalState && initialState?.url) || showDelete"
          class="d-flex justify-center align-center"
        >
          <div v-if="!internalState && initialState?.url" class="mr-1">
            <slot name="append-outer" :file-url="initialState?.url" />
          </div>
          <icon-button
            v-if="showDelete"
            @click.stop="clearOrDelete"
            icon-text="$deleteContent"
            i18n-key="actions.delete"
          />
        </div>
      </v-expand-x-transition>
    </template>
  </v-file-input>
</template>

<script>
import formRulesMixin from "../../../mixins/formRulesMixin";

export default {
  name: "FileField",
  extends: "v-file-input",
  mixins: [formRulesMixin],
  data() {
    return {
      internalState: null,
      initialState: undefined,
    };
  },
  props: {
    value: {
      type: [File, Object],
      default: undefined,
    },
  },
  watch: {
    value: {
      handler(newValue) {
        if (this.initialState === undefined) {
          this.initialState = newValue;
        }
        if (newValue instanceof File || newValue == null) {
          this.internalState = newValue;
        }
        this.emitInput();
      },
      deep: true,
      immediate: true,
    },
    internalState: {
      handler() {
        this.emitInput();
      },
      deep: true,
    },
  },
  methods: {
    emitInput() {
      this.$emit("input", this.internalState);
    },
    clearOrDelete() {
      if (
        this.internalState instanceof File &&
        this.internalState != this.initialState
      ) {
        this.internalState = undefined;
      } else if (this.initialState) {
        this.internalState = null;
        this.initialState = undefined;
      }
    },
  },
  computed: {
    showClear() {
      if (Object.hasOwn(this.$attrs, "clearable") && !this.$attrs.clearable) {
        return false;
      }
      return this.internalState instanceof File;
    },
    showDelete() {
      if (Object.hasOwn(this.$attrs, "clearable") && !this.$attrs.clearable) {
        return false;
      }
      return (
        !(this.internalState instanceof File) &&
        !!this.initialState &&
        this?.initialState.name
      );
    },
    hint() {
      if (!(this.initialState instanceof File) && this.initialState?.name) {
        return this.$t("forms.file.hint", {
          fileName: this.initialState?.name,
        });
      }
      return null;
    },
  },
};
</script>

<style scoped></style>
