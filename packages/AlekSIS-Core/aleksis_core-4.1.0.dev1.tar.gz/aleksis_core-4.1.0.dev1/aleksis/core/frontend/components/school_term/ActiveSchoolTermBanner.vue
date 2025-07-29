<script>
export default {
  name: "ActiveSchoolTermBanner",
};
</script>

<template>
  <v-banner
    :single-line="!$vuetify.breakpoint.mobile"
    v-bind="$attrs"
    v-on="$listeners"
    color="warning white--text"
    icon="$warning"
    icon-color="white"
    id="banner"
  >
    {{
      $t("school_term.active_school_term.warning", {
        termName: $root.activeSchoolTerm?.name,
      })
    }}

    <template #actions>
      <v-btn text color="black" @click="$root.activeSchoolTerm = null">
        {{ $t("school_term.active_school_term.select_action") }}
      </v-btn>
    </template>
  </v-banner>
</template>

<style>
#banner > .v-banner__wrapper {
  padding-block: 4px;
}
</style>
