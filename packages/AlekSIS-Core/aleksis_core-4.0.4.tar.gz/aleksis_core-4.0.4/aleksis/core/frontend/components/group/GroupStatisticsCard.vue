<script>
export default {
  name: "GroupStatisticsCard",
  props: {
    group: {
      type: Object,
      required: true,
    },
  },
};
</script>

<template>
  <v-card>
    <v-card-title>{{ $t("group.statistics.title") }}</v-card-title>

    <v-list>
      <v-list-item>
        <v-list-item-icon>
          <v-icon>mdi-file-account-outline</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title>
            {{ $tc("group.statistics.members_n", group.statistics.members) }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-divider inset />

      <v-list-item
        v-if="group.statistics.ageRangeMin !== group.statistics.ageRangeMax"
      >
        <v-list-item-icon>
          <v-icon>mdi-calendar-range-outline</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title>
            {{
              $t("group.statistics.age_range_from_to", {
                min: group.statistics.ageRangeMin,
                max: group.statistics.ageRangeMax,
              })
            }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ $t("group.statistics.age_range") }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider inset />

      <v-list-item>
        <v-list-item-icon>
          <v-icon>mdi-cake-variant-outline</v-icon>
        </v-list-item-icon>

        <v-list-item-content>
          <v-list-item-title>
            {{
              $tc("time.years_n", group.statistics.ageAvg, {
                n: $n(group.statistics.ageAvg),
              })
            }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ $t("group.statistics.age_average") }}
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-card>
</template>

<style scoped></style>
