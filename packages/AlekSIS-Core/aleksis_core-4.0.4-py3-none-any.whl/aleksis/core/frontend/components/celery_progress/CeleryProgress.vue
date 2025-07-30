<!-- Display the progress/status of a background task on the server -->

<template>
  <small-container>
    <v-card :loading="$apollo.loading">
      <celery-progress-inner :task-id="$route.params.taskId" />
    </v-card>
  </small-container>
</template>

<script>
import CeleryProgressInner from "./CeleryProgressInner.vue";

export default {
  name: "CeleryProgress",
  components: { CeleryProgressInner },
};
</script>
