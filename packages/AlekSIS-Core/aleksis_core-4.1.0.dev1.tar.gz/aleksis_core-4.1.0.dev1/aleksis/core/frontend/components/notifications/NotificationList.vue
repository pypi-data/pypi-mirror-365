<template>
  <v-menu
    offset-y
    :close-on-content-click="false"
    max-width="min(600px, 80vw)"
    width="min-content"
    max-height="90%"
  >
    <template #activator="{ on, attrs }">
      <v-btn
        icon
        dark
        v-bind="attrs"
        v-on="on"
        :loading="$apollo.queries.myNotifications.loading"
        class="mx-2"
        :aria-label="$t('actions.list_notifications')"
      >
        <v-icon
          v-if="
            myNotifications &&
            myNotifications.person &&
            unreadNotifications.length > 0
          "
        >
          mdi-bell-badge-outline
        </v-icon>
        <v-icon color="white" v-else>mdi-bell-outline</v-icon>
      </v-btn>
    </template>
    <v-list nav three-line dense class="overflow-y-auto">
      <v-skeleton-loader
        v-if="$apollo.queries.myNotifications.loading"
        class="mx-auto"
        type="paragraph"
      ></v-skeleton-loader>
      <template
        v-else-if="
          myNotifications.person &&
          myNotifications.person.notifications &&
          myNotifications.person.notifications.length
        "
      >
        <ApolloMutation
          :mutation="markAllNotificationsReadMutation"
          :refetch-queries="myNotificationsQuery"
        >
          <template #default="{ mutate, loading, error }">
            <v-subheader>
              {{ $t("notifications.notifications") }}
              <v-spacer v-if="unreadNotifications.length" />
              <icon-button
                v-if="unreadNotifications.length"
                icon-text="mdi-email-multiple-outline"
                color="secondary"
                i18n-key="notifications.mark_all_as_read"
                @click="() => mutate()"
                :loading="loading"
              />
            </v-subheader>
          </template>
        </ApolloMutation>
        <template v-for="notification in myNotifications.person.notifications">
          <NotificationItem
            :key="notification.id"
            :notification="notification"
          />
          <v-divider
            v-if="
              notification !==
              myNotifications.person.notifications[
                myNotifications.person.notifications.length - 1
              ]
            "
            :key="notification.id + '-divider'"
          ></v-divider>
        </template>
      </template>
      <v-list-item v-else value="empty">
        <div class="d-flex justify-center align-center flex-column">
          <div class="mb-4">
            <mascot type="no_notifications" width="min(200px, 30vw)" />
          </div>
          <div>{{ $t("notifications.no_notifications") }}</div>
        </div>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import NotificationItem from "./NotificationItem.vue";
import gqlMyNotifications from "./myNotifications.graphql";
import Mascot from "../generic/mascot/Mascot.vue";
import { markAllNotificationsRead } from "./markAllNotificationsRead.graphql";

export default {
  components: {
    Mascot,
    NotificationItem,
  },
  apollo: {
    myNotifications: {
      query: gqlMyNotifications,
      pollInterval: 30000,
    },
  },
  computed: {
    unreadNotifications() {
      return this.myNotifications.person.notifications
        ? this.myNotifications.person.notifications.filter((n) => !n.read)
        : [];
    },
    myNotificationsQuery() {
      return () => [{ query: gqlMyNotifications }];
    },
  },
  data() {
    return {
      markAllNotificationsReadMutation: markAllNotificationsRead,
    };
  },
};
</script>
