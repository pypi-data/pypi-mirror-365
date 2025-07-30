<script>
import {
  activeSchoolTerm,
  schoolTermsForActiveSchoolTerm,
  setActiveSchoolTerm,
} from "./activeSchoolTerm.graphql";
import loadingMixin from "../../mixins/loadingMixin";
export default {
  name: "ActiveSchoolTermSelect",
  mixins: [loadingMixin],
  apollo: {
    schoolTerms: {
      query: schoolTermsForActiveSchoolTerm,
    },
    activeSchoolTerm: {
      query: activeSchoolTerm,
      result() {
        this.$emit("input", this.activeSchoolTerm);
      },
    },
  },
  props: {
    affectedQuery: {
      type: Number,
      default: 0,
    },
    value: {
      type: Object,
      required: false,
      default: null,
    },
    disableInvalidate: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data() {
    return {
      activeSchoolTerm: null,
      schoolTerms: [],
      showSuccess: false,
    };
  },
  computed: {
    schoolTerm: {
      get() {
        return this.activeSchoolTerm?.id;
      },
      set(value) {
        if (this.activeSchoolTerm?.id === value) {
          return;
        }

        this.handleLoading(true);

        this.$apollo
          .mutate({
            mutation: setActiveSchoolTerm,
            variables: { id: value },
            update: (store, data) => {
              const newTerm = data.data.setActiveSchoolTerm;

              // Update cached data
              store.writeQuery({ query: activeSchoolTerm, data: newTerm });
              this.$emit("input", newTerm);
            },
          })
          .catch((error) => {
            this.handleMutationError(error);
          })
          .finally(() => {
            this.handleLoading(false);
            this.showSuccess = true;
            setTimeout(() => {
              this.showSuccess = false;
            }, 2000);

            if (!this.disableInvalidate) {
              this.$invalidateState();
            }
          });
      },
    },
  },
  watch: {
    value(value) {
      if (!value) {
        value = this.schoolTerms.find((term) => term.current);
      }
      if (Object.hasOwn(value, "activeSchoolTerm")) {
        value = value.activeSchoolTerm;
      }
      if (Object.hasOwn(value, "id")) {
        value = value.id;
      }

      if (this.schoolTerm === value) {
        return;
      }

      this.schoolTerm = value;
    },
  },
};
</script>

<template>
  <v-menu offset-y :close-on-content-click="false">
    <template #activator="{ on, attrs }">
      <v-btn
        icon
        dark
        v-bind="{ ...$attrs, ...attrs }"
        v-on="on"
        :loading="$apollo.queries.activeSchoolTerm.loading"
        :aria-label="$t('actions.select_school_term')"
      >
        <v-icon v-if="activeSchoolTerm?.current">$schoolTerm</v-icon>
        <v-icon v-else>mdi-calendar-alert-outline</v-icon>
      </v-btn>
    </template>
    <v-list :disabled="loading">
      <v-list-item disabled>
        <v-list-item-content>
          <v-list-item-title>
            {{ $t("school_term.active_school_term.title") }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ $t("school_term.active_school_term.subtitle") }}
          </v-list-item-subtitle>
        </v-list-item-content>

        <v-avatar>
          <v-progress-circular
            v-if="loading"
            indeterminate
            :size="16"
            :width="2"
          />
          <v-icon v-else-if="showSuccess" color="success">$success</v-icon>
        </v-avatar>
      </v-list-item>

      <v-list-item-group v-model="schoolTerm" :mandatory="!!activeSchoolTerm">
        <v-list-item
          v-for="term in schoolTerms"
          :key="term.id"
          :value="term.id"
        >
          <v-list-item-content>
            <v-list-item-title>
              {{ term.name }}
            </v-list-item-title>
          </v-list-item-content>

          <v-list-item-action v-if="term.current">
            <v-chip label color="secondary">
              {{ $t("school_term.current") }}
            </v-chip>
          </v-list-item-action>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-menu>
</template>
