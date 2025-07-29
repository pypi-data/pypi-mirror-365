<script>
import previewMixin from "../previewMixin";

export default {
  name: "Preview",
  mixins: [previewMixin],
};
</script>

<template>
  <v-card>
    <v-skeleton-loader boilerplate type="image" />

    <v-card-actions>
      <v-btn color="primary" text disabled>
        {{ widget.title }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
