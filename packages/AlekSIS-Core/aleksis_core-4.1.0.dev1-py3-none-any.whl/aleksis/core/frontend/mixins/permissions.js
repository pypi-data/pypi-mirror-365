/**
 * Vue mixin containing permission checking code.
 */

const permissionsMixin = {
  methods: {
    isPermissionFetched(permissionName) {
      return (
        this.$root.permissions &&
        this.$root.permissions.find((p) => p.name === permissionName)
      );
    },
    checkPermission(permissionName) {
      return (
        this.isPermissionFetched(permissionName) &&
        this.$root.permissions.find((p) => p.name === permissionName).result
      );
    },
    addPermissions(newPermissionNames) {
      this.$root.permissionNames = [
        ...new Set([...this.$root.permissionNames, ...newPermissionNames]),
      ];
    },
    checkObjectPermission(name, objId, objType, appLabel) {
      if (this.$root.objectPermissions) {
        const permissionItem = this.$root.objectPermissions.find(
          (p) =>
            p.name === name &&
            p.objId === objId &&
            p.objType === objType &&
            p.appLabel === appLabel,
        );
        if (permissionItem) {
          return permissionItem.result;
        }
      }
      return false;
    },
    addObjectPermission(name, objId, objType, appLabel) {
      const newPermissionItem = {
        name: name,
        objId: objId,
        objType: objType,
        appLabel: appLabel,
      };
      const mergedObjectPermissionArray = Array.from(
        new Set(
          [...this.$root.objectPermissionItems, newPermissionItem].map((o) =>
            JSON.stringify(o),
          ),
        ),
      );

      this.$root.objectPermissionItems = mergedObjectPermissionArray.map(
        (str) => JSON.parse(str),
      );
    },
  },
};

export default permissionsMixin;
