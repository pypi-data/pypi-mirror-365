<script>
import { deleteGroups } from "../groups.graphql";
import DeleteDialog from "../../generic/dialogs/DeleteDialog.vue";
import groupActionsMixin from "./groupActionsMixin";

export default {
  name: "DeleteGroup",
  components: { DeleteDialog },
  mixins: [groupActionsMixin],
  data() {
    return {
      showDeleteConfirm: false,
      deleteMutation: deleteGroups,
    };
  },
};
</script>

<template>
  <v-list-item @click="showDeleteConfirm = true" class="error--text">
    <v-list-item-icon>
      <v-icon color="error">$deleteContent</v-icon>
    </v-list-item-icon>
    <v-list-item-content>
      <v-list-item-title>
        {{ $t("actions.delete") }}
      </v-list-item-title>
    </v-list-item-content>

    <delete-dialog
      v-model="showDeleteConfirm"
      :gql-delete-mutation="deleteMutation"
      item-attribute="name"
      :items="[group]"
      @save="
        $router.push({
          name: 'core.groups',
        })
      "
    >
      <template #title>
        {{ $t("group.confirm_delete") }}
      </template>
    </delete-dialog>
  </v-list-item>
</template>

<style scoped></style>
