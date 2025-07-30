<script setup>
import GroupCollection from "./GroupCollection.vue";
</script>
<script>
export default {
  name: "GroupPropertiesCard",
  props: {
    group: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <v-card>
    <v-card-title>{{ $t("group.properties") }}</v-card-title>

    <v-list two-line>
      <v-list-item>
        <v-list-item-icon>
          <v-icon>$groupType</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title>
            {{ group.groupType?.name || $t("group.group_type.no_group_type") }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ $t("group.group_type.title") }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider inset />
    </v-list>

    <v-list-group
      :disabled="group.childGroups.length === 0"
      :append-icon="group.childGroups.length === 0 ? null : undefined"
    >
      <template #activator>
        <v-list-item-icon>
          <v-icon>mdi-subdirectory-arrow-right</v-icon>
        </v-list-item-icon>
        <v-list-item-title>{{
          $tc("group.child_groups_n", group.childGroups.length)
        }}</v-list-item-title>
      </template>
      <group-collection :groups="group.childGroups" dense />
    </v-list-group>

    <v-list-group
      :disabled="group.parentGroups.length === 0"
      :append-icon="group.parentGroups.length === 0 ? null : undefined"
    >
      <template #activator>
        <v-list-item-icon>
          <v-icon>mdi-file-tree-outline</v-icon>
        </v-list-item-icon>
        <v-list-item-title>{{
          $tc("group.parent_groups_n", group.parentGroups.length)
        }}</v-list-item-title>
      </template>
      <group-collection :groups="group.parentGroups" />
    </v-list-group>
  </v-card>
</template>

<style scoped></style>
