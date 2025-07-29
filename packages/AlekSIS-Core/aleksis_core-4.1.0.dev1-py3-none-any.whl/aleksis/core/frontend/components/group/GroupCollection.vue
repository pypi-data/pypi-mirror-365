<template>
  <v-list v-if="groups.length">
    <v-list-item
      v-for="group in groups"
      :key="group.id"
      :to="{ name: 'core.group', params: { id: group.id } }"
    >
      <v-list-item-avatar v-if="group.avatarUrl">
        <avatar-content v-if="group.avatarUrl" :image-url="group.avatarUrl" />
      </v-list-item-avatar>
      <v-list-item-action v-else />

      <v-list-item-content>
        <v-list-item-title>
          {{ group.name }}
          <span v-if="group.schoolTerm && group.schoolTerm.name">
            ({{ group.schoolTerm.name }})
          </span>
        </v-list-item-title>
      </v-list-item-content>
    </v-list-item>
  </v-list>
  <v-list v-else>
    <v-list-item>
      <v-list-item-content>
        <v-list-item-title>
          {{ $t("group.no_groups") }}
        </v-list-item-title>
      </v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
import AvatarContent from "../person/AvatarContent.vue";

export default {
  name: "GroupList",
  components: { AvatarContent },
  props: {
    groups: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style scoped></style>
