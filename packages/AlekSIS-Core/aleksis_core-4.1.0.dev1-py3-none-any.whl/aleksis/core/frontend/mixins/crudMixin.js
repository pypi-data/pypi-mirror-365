/**
 * This mixin provides shared crud props.
 */
export default {
  props: {
    /**
     * Enable editing of items
     * via the create component (defaults to DialogObjectForm)
     * @values true, false
     */
    enableEdit: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
};
