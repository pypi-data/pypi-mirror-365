<script>
export default {
  name: "RoomChip",
  props: {
    room: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <v-tooltip bottom>
    <template #activator="{ on, attrs }">
      <v-chip v-bind="{ ...attrs, ...$attrs }" v-on="{ ...on, ...$listeners }">
        <v-avatar>
          <v-icon> mdi-door </v-icon>
        </v-avatar>
        {{ room.shortName }}
      </v-chip>
    </template>
    <span>{{ room.name }}</span>
  </v-tooltip>
</template>
