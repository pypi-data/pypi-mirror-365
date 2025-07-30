/*
 * Plugin to collect AlekSIS-specific Vue utilities.
 */

// aleksisAppImporter is a virtual module defined in Vite config
import { appMessages } from "aleksisAppImporter";
import aleksisMixin from "../mixins/aleksis.js";
import * as langs from "@/vuetify/src/locale";
import { DateTime } from "luxon";

console.debug("Defining AleksisVue plugin");
const AleksisVue = {};

AleksisVue.install = function (Vue) {
  /*
   * The browser title when the app was loaded.
   *
   * Thus, it is injected from Django in the vue_index template.
   */
  Vue.$pageBaseTitle = document.title;

  Vue.$aleksisFrontendSettings = JSON.parse(
    document.getElementById("frontend_settings").textContent,
  );

  /**
   * Configure Sentry if desired.
   *
   * It depends on Sentry settings being passed as a DOM object by Django
   * in the vue_index template.
   */
  Vue.$configureSentry = function (router) {
    if (Vue.$aleksisFrontendSettings.sentry.enabled) {
      import("../app/sentry.js").then((mod) => {
        mod.default.Sentry.init({
          Vue,
          dsn: Vue.$aleksisFrontendSettings.sentry.dsn,
          environment: Vue.$aleksisFrontendSettings.sentry.environment,
          tracesSampleRate:
            Vue.$aleksisFrontendSettings.sentry.traces_sample_rate,
          logError: true,
          integrations: [
            new mod.default.BrowserTracing({
              routingInstrumentation:
                mod.default.Sentry.vueRouterInstrumentation(router),
            }),
          ],
        });
      });
    }
  };

  /**
   * Register all global components that shall be reusable by apps.
   */
  Vue.$registerGlobalComponents = function () {
    const globalComponents = {
      // General stuff
      AvatarClickbox: import("../components/generic/AvatarClickbox.vue"),
      CalendarWithControls: import(
        "../components/calendar/CalendarWithControls.vue"
      ),
      ErrorPage: import("../components/app/ErrorPage.vue"),
      MessageBox: import("../components/generic/MessageBox.vue"),
      SmallContainer: import("../components/generic/SmallContainer.vue"),

      // Layout
      DetailView: import("../components/generic/DetailView.vue"),
      ListView: import("../components/generic/ListView.vue"),

      // Buttons:
      BackButton: import("../components/generic/BackButton.vue"),
      ButtonMenu: import("../components/generic/ButtonMenu.vue"),
      CancelButton: import("../components/generic/buttons/CancelButton.vue"),
      CreateButton: import("../components/generic/buttons/CreateButton.vue"),
      DeleteButton: import("../components/generic/buttons/DeleteButton.vue"),
      DialogCloseButton: import(
        "../components/generic/buttons/DialogCloseButton.vue"
      ),
      EditButton: import("../components/generic/buttons/EditButton.vue"),
      FabButton: import("../components/generic/buttons/FabButton.vue"),
      FilterButton: import("../components/generic/buttons/FilterButton.vue"),
      IconButton: import("../components/generic/buttons/IconButton.vue"),
      PrimaryActionButton: import(
        "../components/generic/buttons/PrimaryActionButton.vue"
      ),
      SaveButton: import("../components/generic/buttons/SaveButton.vue"),
      SecondaryActionButton: import(
        "../components/generic/buttons/SecondaryActionButton.vue"
      ),
    };

    for (let [name, module] of Object.entries(globalComponents)) {
      Vue.component(name, () => module);
    }
  };

  /**
   * Set the page title.
   *
   * This will automatically add the base title discovered at app loading time.
   *
   * @param {string} title Specific title to set, or null.
   * @param {Object} route Route to discover title from, or null.
   */
  Vue.prototype.$setPageTitle = function (title, route) {
    let titleParts = [];

    if (title) {
      titleParts.push(title);
    } else {
      if (!route) {
        route = this.$route;
      }
      if (route.meta.titleKey) {
        titleParts.push(this.$t(route.meta.titleKey));
      }
    }

    titleParts.push(Vue.$pageBaseTitle);
    const newTitle = titleParts.join(" – ");
    console.debug(`Setting page title: ${newTitle}`);
    document.title = newTitle;
  };

  /**
   * Set the toolbar title visible on the page.
   *
   * This will automatically add the base title discovered at app loading time.
   *
   * @param {string} title Specific title to set, or null.
   * @param {Object} route Route to discover title from, or null.
   */
  Vue.prototype.$setToolBarTitle = function (title, route) {
    let newTitle;

    if (title) {
      newTitle = title;
    } else {
      if (!route) {
        route = this.$route;
      }
      if (route.meta.toolbarTitle) {
        newTitle = this.$t(route.meta.toolbarTitle);
      }
    }

    newTitle = newTitle || Vue.$pageBaseTitle;
    console.debug(`Setting toolbar title: ${newTitle}`);
    this.$root.toolbarTitle = newTitle;
  };

  /**
   * Get base title defined by current Instance
   * @return {string} Title as defined in site preferences
   */
  Vue.prototype.$getBaseTitle = function () {
    return Vue.$pageBaseTitle;
  };

  /**
   * Load i18n messages from all known AlekSIS apps.
   */
  Vue.prototype.$loadAppMessages = function () {
    for (const messages of Object.values(appMessages)) {
      for (let locale in messages) {
        this.$i18n.mergeLocaleMessage(locale, messages[locale]);
      }
    }
  };

  /**
   * Load vuetifys built-in translations
   */
  Vue.prototype.$loadVuetifyMessages = function () {
    for (const [locale, messages] of Object.entries(langs)) {
      this.$i18n.mergeLocaleMessage(locale, { $vuetify: messages });
    }
  };

  /**
   * Invalidate state and force reload from server.
   *
   * Mostly useful after the user context changes by login/logout/impersonate.
   */
  Vue.prototype.$invalidateState = function () {
    console.info("Invalidating application state");

    this.invalidation = true;

    this.$apollo
      .getClient()
      .resetStore()
      .then(
        () => {
          console.info("GraphQL cache cleared");
          this.invalidation = false;
        },
        (error) => {
          console.error("Could not clear GraphQL cache:", error);
          this.invalidation = false;
        },
      );
  };

  /**
   * Add navigation guards to account for global loading state and page titles.
   */
  Vue.prototype.$setupNavigationGuards = function () {
    const vm = this;

    // eslint-disable-next-line no-unused-vars
    this.$router.afterEach((to, from, next) => {
      console.debug("Setting new page title due to route change");
      vm.$setPageTitle(null, to);
      vm.$setToolBarTitle(null, to);
    });

    // eslint-disable-next-line no-unused-vars
    this.$router.beforeEach((to, from, next) => {
      vm.contentLoading = true;
      next();
    });

    // eslint-disable-next-line no-unused-vars
    this.$router.afterEach((to, from) => {
      if (vm.isLegacyBaseTemplate) {
        // Skip resetting loading state for legacy pages
        // as they are probably not finished with loading yet
        // LegacyBaseTemplate will reset the loading state later
        return;
      }
      vm.contentLoading = false;
    });

    // eslint-disable-next-line no-unused-vars
    this.$router.beforeEach((to, from, next) => {
      if (from.meta.invalidate === "leave" || to.meta.invalidate === "enter") {
        console.debug("Route requests to invalidate state");
        vm.$invalidateState();
      }
      next();
    });
  };

  Vue.prototype.$d = function (value, ...args) {
    if (typeof value === DateTime) {
      value = value.toJSDate();
    }
    return this.$i18n.d(value, ...args);
  };

  /**
   * Activate frequent polling for celery task progress.
   *
   * This can be used to notify the frontend about a currently running task that
   * should be monitored more closely.
   *
   */
  Vue.prototype.$activateFrequentCeleryPolling = function () {
    console.debug("Activate frequent polling for Celery tasks");
    this.$root.frequentCeleryPolling = true;
  };

  // Add default behaviour for all components
  Vue.mixin(aleksisMixin);
};

export default AleksisVue;
