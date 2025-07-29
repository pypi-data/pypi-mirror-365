<script setup>
import MainCalendarEventDialog from "../../calendar/MainCalendarEventDialog.vue";
</script>

<template>
  <main-calendar-event-dialog
    v-bind="$attrs"
    v-on="$listeners"
    initial-selected-event="personalTodo"
    :selectable-events="['personalTodo']"
    @save="$emit('refreshCalendar')"
  >
    <template #activator="{ attrs, on }">
      <slot name="activator" :attrs="attrs" :on="on" />
    </template>
  </main-calendar-event-dialog>
</template>

<script>
export default {
  name: "PersonalTodoForm",
  extends: MainCalendarEventDialog,
  emits: ["refreshCalendar"],
};
</script>
