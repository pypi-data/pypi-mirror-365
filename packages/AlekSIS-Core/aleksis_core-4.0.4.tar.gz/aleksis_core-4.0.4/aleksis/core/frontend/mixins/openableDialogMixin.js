export default {
  props: {
    /**
     * Dialog state (open or closed)
     * @model
     * @values true,false
     */
    value: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["input"],
};
