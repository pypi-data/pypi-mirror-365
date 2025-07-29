import gqlCustomMenu from "../components/app/customMenu.graphql";

import permissionsMixin from "./permissions.js";

/**
 * Vue mixin containing menu generation code.
 *
 * Only used by main App component, but factored out for readability.
 */
const menusMixin = {
  mixins: [permissionsMixin],
  data() {
    return {
      footerMenu: null,
      sideNavMenu: null,
      accountMenu: null,
    };
  },
  methods: {
    getPermissionNames() {
      let permArray = [];

      for (const route of this.$router.getRoutes()) {
        if (route.meta) {
          if (
            route.meta["permission"] &&
            !(route.meta["permission"] in permArray)
          ) {
            permArray.push(route.meta["permission"]);
          }
          if (
            route.meta["menuPermission"] &&
            !(route.meta["menuPermission"] in permArray)
          ) {
            permArray.push(route.meta["menuPermission"]);
          }
        }
      }

      this.addPermissions(permArray);
    },
    buildMenu(routes, menuKey) {
      let menu = {};

      // Top-level entries
      for (const route of routes) {
        if (
          route.name &&
          route.meta &&
          route.meta[menuKey] &&
          !route.parent &&
          (route.meta.menuPermission
            ? this.checkPermission(route.meta.menuPermission)
            : route.meta.permission
              ? this.checkPermission(route.meta.permission)
              : true) &&
          (route.meta.validators
            ? this.checkValidators(route.meta.validators)
            : true) &&
          !route.meta.hide
        ) {
          let menuItem = {
            ...route.meta,
            name: route.name,
            path: route.path,
            subMenu: [],
          };
          menu[menuItem.name] = menuItem;
        }
      }

      // Sub menu entries
      for (const route of routes) {
        let parentName = route.parent?.name || "";
        // Put object routes into their normal app menu
        if (parentName.startsWith("objects.")) {
          parentName = parentName.slice("objects.".length);
        }
        if (
          route.name &&
          route.meta &&
          route.meta[menuKey] &&
          route.parent &&
          parentName &&
          parentName in menu &&
          (route.meta.menuPermission
            ? this.checkPermission(route.meta.menuPermission)
            : route.meta.permission
              ? this.checkPermission(route.meta.permission)
              : true) &&
          (route.meta.validators
            ? this.checkValidators(route.meta.validators)
            : true) &&
          !route.meta.hide
        ) {
          let menuItem = {
            ...route.meta,
            name: route.name,
            path: route.path,
            subMenu: [],
          };
          menu[parentName].subMenu.push(menuItem);
        }
      }

      return Object.values(menu);
    },
    checkValidators(validators) {
      for (const validator of validators) {
        if (!validator(this.whoAmI, this.systemProperties)) {
          return false;
        }
      }
      return true;
    },
    buildMenus() {
      this.accountMenu = this.buildMenu(
        this.$router.getRoutes(),
        "inAccountMenu",
      );
      this.sideNavMenu = this.buildMenu(this.$router.getRoutes(), "inMenu");
    },
  },
  apollo: {
    footerMenu: {
      query: gqlCustomMenu,
      variables() {
        return {
          name: "footer",
        };
      },
      update: (data) => data.customMenuByName,
    },
  },
  mounted() {
    this.$router.onReady(this.getPermissionNames);
    this.buildMenus();
  },
};

export default menusMixin;
