export default {
  props: {
    /**
     * Dialog-mode (open or closed)
     * @model
     * @values true,false
     */
    value: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  emits: ["input"],
  data() {
    return {
      internalDialogMode: this.value,
    };
  },
  computed: {
    dialogMode: {
      get() {
        return this.internalDialogMode;
      },
      set(newValue) {
        this.internalDialogMode = newValue;
        this.$emit("input", newValue);
      },
    },
  },
  mounted() {
    this.$watch("value", (newVal) => {
      this.dialogMode = newVal;
    });
  },
};
