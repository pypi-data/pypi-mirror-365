<script setup>
import ForeignKeyField from "../../generic/forms/ForeignKeyField.vue";
import RoomChip from "../../room/RoomChip.vue";
import CreateRoom from "../../room/CreateRoom.vue";
</script>

<template>
  <foreign-key-field
    v-bind="$attrs"
    v-on="$listeners"
    :fields="headers"
    create-item-i18n-key="rooms.create_room"
    :gql-query="gqlQuery"
    :gql-create-mutation="gqlCreateMutation"
    :gql-patch-mutation="gqlPatchMutation"
    :default-item="defaultItem"
  >
    <template #item="{ item }">
      <room-chip :room="item" />
    </template>
    <template #createComponent="{ attrs, on }">
      <create-room v-bind="attrs" v-on="on" />
    </template>
  </foreign-key-field>
</template>

<script>
import { rooms, createRooms, updateRooms } from "../../room/room.graphql";

export default {
  name: "RoomField",
  extends: "foreign-key-field",
  data() {
    return {
      headers: [
        {
          text: this.$t("rooms.name"),
          value: "name",
        },
        {
          text: this.$t("rooms.short_name"),
          value: "shortName",
        },
      ],
      gqlQuery: rooms,
      gqlCreateMutation: createRooms,
      gqlPatchMutation: updateRooms,
      defaultItem: {
        name: "",
        shortName: "",
      },
    };
  },
};
</script>
