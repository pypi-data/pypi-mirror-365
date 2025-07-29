<template>
  <v-sheet class="fullsize" @click="$emit('toggle')" :outlined="selected">
    <v-overlay absolute :value="selected">
      <div class="grid">
        <div class="up">
          <primary-action-button
            @click="resize(0, -1, 0, 1)"
            icon
            :disabled="!canGoUp"
            icon-text="mdi-arrow-expand-up"
            i18n-key="actions.expand.up"
          />
          <primary-action-button
            @click="resize(0, 1, 0, -1)"
            icon
            :disabled="widget.h <= 1"
            icon-text="mdi-arrow-collapse-down"
            i18n-key="actions.collapse.down"
          />
        </div>

        <div class="left">
          <primary-action-button
            @click="resize(-1, 0, 1, 0)"
            icon
            :disabled="!canGoLeft"
            icon-text="mdi-arrow-expand-left"
            i18n-key="actions.expand.left"
          />
          <primary-action-button
            @click="resize(1, 0, -1, 0)"
            icon
            :disabled="widget.w <= 1"
            icon-text="mdi-arrow-collapse-right"
            i18n-key="actions.collapse.right"
          />
        </div>

        <div class="delete">
          <secondary-action-button
            icon
            small
            color="error"
            fab
            i18n-key="actions.delete"
            icon-text="$deleteContent"
            fixed
            :loading="loading"
            @click="performDelete"
          />
        </div>
        <div class="right">
          <primary-action-button
            @click="resize(0, 0, 1, 0)"
            icon
            :disabled="!canGoRight"
            icon-text="mdi-arrow-expand-right"
            i18n-key="actions.expand.right"
          />
          <primary-action-button
            @click="resize(0, 0, -1, 0)"
            icon
            :disabled="widget.w <= 1"
            icon-text="mdi-arrow-collapse-left"
            i18n-key="actions.collapse.left"
          />
        </div>
        <div class="down">
          <primary-action-button
            @click="resize(0, 0, 0, 1)"
            icon
            :disabled="!canGoDown"
            icon-text="mdi-arrow-expand-down"
            i18n-key="actions.expand.down"
          />
          <primary-action-button
            @click="resize(0, 0, 0, -1)"
            icon
            :disabled="widget.h <= 1"
            icon-text="mdi-arrow-collapse-up"
            i18n-key="actions.collapse.up"
          />
        </div>
      </div>
    </v-overlay>

    <component :is="component" v-bind="widget.data" class="fullsize" />
  </v-sheet>
</template>

<script>
import deleteMixin from "../../../mixins/deleteMixin";

export default {
  name: "MovableWidget",
  emits: ["toggle", "reposition"],
  mixins: [deleteMixin],
  props: {
    widget: {
      type: Object,
      required: true,
    },
    selected: {
      type: Boolean,
      required: false,
      default: false,
    },
    component: {
      type: [String, Object, Function],
      required: true,
    },
    positionAllowed: {
      type: [Function],
      required: false,
      default: (x, y, key) => false,
    },
  },
  methods: {
    performDelete() {
      this.delete([this.widget.data]);
    },
    resize(deltaX, deltaY, deltaW, deltaH) {
      this.$emit("reposition", {
        ...this.widget,
        x: this.widget.x + deltaX,
        y: this.widget.y + deltaY,
        w: this.widget.w + deltaW,
        h: this.widget.h + deltaH,
      });
    },
  },
  computed: {
    canGoLeft() {
      const x = this.widget.x - 1;
      for (let yOffset = 0; yOffset < this.widget.h; yOffset++) {
        let y = this.widget.y + yOffset;
        if (!this.positionAllowed(x, y, this.widget.key)) {
          return false;
        }
      }

      return true;
    },
    canGoRight() {
      const x = this.widget.x + this.widget.w;
      for (let yOffset = 0; yOffset < this.widget.h; yOffset++) {
        let y = this.widget.y + yOffset;
        if (!this.positionAllowed(x, y, this.widget.key)) {
          return false;
        }
      }

      return true;
    },
    canGoUp() {
      const y = this.widget.y - 1;
      for (let xOffset = 0; xOffset < this.widget.w; xOffset++) {
        let x = this.widget.x + xOffset;
        if (!this.positionAllowed(x, y, this.widget.key)) {
          return false;
        }
      }

      return true;
    },
    canGoDown() {
      const y = this.widget.y + this.widget.h;
      for (let xOffset = 0; xOffset < this.widget.w; xOffset++) {
        let x = this.widget.x + xOffset;
        if (!this.positionAllowed(x, y, this.widget.key)) {
          return false;
        }
      }

      return true;
    },
  },
};
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  grid-template-rows: 1fr 2fr 1fr;
  grid-template-areas: ". up ." "left delete right" ". down .";
}
.grid > div {
  display: flex;
  align-items: center;
  justify-content: center;
}
.grid > .left,
.grid > .right {
  flex-direction: column;
}
.grid > .up {
  grid-area: up;
}
.grid > .down {
  grid-area: down;
}
.grid > .left {
  grid-area: left;
}
.grid > .right {
  grid-area: right;
}
.grid > .delete {
  grid-area: delete;
}
</style>
