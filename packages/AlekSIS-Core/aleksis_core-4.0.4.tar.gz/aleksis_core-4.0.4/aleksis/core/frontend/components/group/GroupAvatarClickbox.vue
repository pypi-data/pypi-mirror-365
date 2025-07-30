<template>
  <avatar-clickbox>
    <template #activator>
      <avatar-content :image-url="url" class="rounded-circle" />
    </template>
    <avatar-content :image-url="url" contain />
  </avatar-clickbox>
</template>

<script>
import AvatarContent from "../person/AvatarContent.vue";

export default {
  name: "GroupAvatarClickBox",
  components: {
    AvatarContent,
  },
  props: {
    url: {
      type: String,
      required: true,
    },
  },
};
</script>
