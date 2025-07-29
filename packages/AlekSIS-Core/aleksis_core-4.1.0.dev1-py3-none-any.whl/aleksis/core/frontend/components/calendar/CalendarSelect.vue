<template>
  <v-list-item-group multiple v-model="model">
    <v-list-item
      v-for="calendarFeed in calendarFeeds"
      :key="calendarFeed.name"
      :value="calendarFeed.name"
      :tabindex="-1"
    >
      <template #default="{ active }">
        <v-list-item-action>
          <v-checkbox
            :input-value="active"
            :color="calendarFeed.color"
            class="focusable"
          ></v-checkbox>
        </v-list-item-action>

        <v-list-item-content>
          <v-list-item-title>
            {{ calendarFeed.verboseName }}
          </v-list-item-title>
        </v-list-item-content>

        <v-list-item-avatar v-if="calendarFeed.componentType === 'todo'">
          <v-icon> mdi-checkbox-multiple-marked-circle-outline </v-icon>
        </v-list-item-avatar>

        <v-list-item-action>
          <button-menu
            icon-only
            :outlined="false"
            icon="mdi-dots-vertical"
            :text="false"
            text-translation-key="actions.more_actions"
          >
            <v-list-item :href="calendarFeed.url">
              <v-list-item-icon>
                <v-icon>mdi-calendar-export</v-icon>
              </v-list-item-icon>
              <v-list-item-title>
                {{ $t("calendar.download_ics") }}
              </v-list-item-title>
            </v-list-item>
          </button-menu>
        </v-list-item-action>
      </template>
    </v-list-item>
  </v-list-item-group>
</template>

<script>
export default {
  name: "CalendarSelect",
  props: {
    calendarFeeds: {
      type: Array,
      required: true,
    },
    value: {
      type: Array,
      required: true,
    },
  },
  computed: {
    model: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
    someSelected() {
      return this.model.length > 0 && !this.allSelected;
    },
    allSelected() {
      return this.model.length === this.calendarFeeds.length;
    },
  },
  methods: {
    toggleAll(newValue) {
      if (newValue) {
        this.model = this.calendarFeeds.map((feed) => feed.name);
      } else {
        this.model = [];
      }
    },
  },
};
</script>
