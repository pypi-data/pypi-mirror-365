<template>
  <v-text-field
    v-bind="$attrs"
    v-on="on"
    :rules="
      $rules()
        .isANumber.isAWholeNumber.isGreaterThan(0)
        .isSmallerThan(32767)
        .build(rules)
    "
    inputmode="numeric"
  >
    <template #append>
      <slot name="append" />
    </template>
  </v-text-field>
</template>

<script>
import formRulesMixin from "../../../mixins/formRulesMixin";

export default {
  name: "PositiveSmallIntegerField",
  extends: "v-text-field",
  mixins: [formRulesMixin],
  props: {
    rules: {
      type: Array,
      required: false,
      default: () => [],
    },
  },
  computed: {
    on() {
      return {
        ...this.$listeners,
        input: this.inputHandler("input"),
        change: this.inputHandler("change"),
      };
    },
  },
  methods: {
    inputHandler(name) {
      return (event) => {
        if (event == null) {
          this.$emit(name, event);
          return;
        }

        const num = parseInt(event.replace(/\D/g, ""));

        if (isNaN(num)) {
          this.$emit(name, null);
          return;
        }

        this.$emit(name, Math.max(0, Math.min(num, 32767)));
      };
    },
  },
};
</script>
