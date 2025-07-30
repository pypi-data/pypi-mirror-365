export const collections = [
  {
    name: "groupOverview",
    type: Object,
    items: [
      {
        tab: {
          id: "default",
          titleKey: "group.tabs.members_tab",
        },
        titleKey: "group.tabs.members",
        component: () => import("./components/group/GroupMembers.vue"),
      },
    ],
  },
  {
    name: "groupActions",
    type: Object,
  },
  {
    name: "personWidgets",
    type: Object,
  },
];

export const collectionItems = {
  coreGroupActions: [
    {
      key: "core-delete-group-action",
      component: () => import("./components/group/actions/DeleteGroup.vue"),
      isActive: (group) => group.canDelete || false,
    },
  ],
};
