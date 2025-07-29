<template>
  <ApolloMutation
    :mutation="require('./markNotificationRead.graphql')"
    :variables="{ id: this.notification.id }"
  >
    <template #default="{ mutate, loading, error }">
      <v-list-item :input-value="!notification.read">
        <v-list-item-avatar>
          <v-icon
            :class="
              notification.read ? 'grey lighten-1' : 'primary white--text'
            "
            dark
          >
            mdi-{{ notification.icon.toLowerCase().replaceAll("_", "-") }}
          </v-icon>
        </v-list-item-avatar>
        <v-list-item-content>
          <v-list-item-title>
            {{ notification.title }}
          </v-list-item-title>

          <v-list-item-subtitle class="font-weight-regular">
            {{ notification.description }}
          </v-list-item-subtitle>

          <v-list-item-subtitle class="caption font-weight-regular">
            <v-chip x-small outlined>{{ notification.sender }}</v-chip>
            ·
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <span v-bind="attrs" v-on="on">{{
                  $d(
                    $parseISODate(notification.created),
                    dateFormat($parseISODate(notification.created)),
                  )
                }}</span>
              </template>
              <span>{{ $d($parseISODate(notification.created), "long") }}</span>
            </v-tooltip>
          </v-list-item-subtitle>
        </v-list-item-content>

        <v-list-item-action>
          <icon-button
            icon-text="mdi-email-outline"
            color="secondary"
            i18n-key="notifications.mark_as_read"
            v-if="!notification.read"
            @click="mutate"
          />

          <icon-button
            icon-text="mdi-open-in-new"
            color="accent"
            i18n-key="notifications.more_information"
            :href="notification.link"
            v-if="notification.link"
          />
        </v-list-item-action>
      </v-list-item>
    </template>
  </ApolloMutation>
</template>

<script>
import { DateTime } from "luxon";

export default {
  props: {
    notification: {
      type: Object,
      required: true,
    },
  },
  methods: {
    dateFormat(date) {
      let now = DateTime.now();
      if (now.hasSame(date, "day")) {
        return "timeOnly";
      } else {
        return "short";
      }
    },
  },
};
</script>
