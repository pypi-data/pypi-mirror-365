<script>
import BaseButton from "./BaseButton.vue";
export default {
  name: "IconButton",
  components: { BaseButton },
  extends: BaseButton,
  props: {
    icon: {
      required: false,
      default: true,
    },
  },
};
</script>
