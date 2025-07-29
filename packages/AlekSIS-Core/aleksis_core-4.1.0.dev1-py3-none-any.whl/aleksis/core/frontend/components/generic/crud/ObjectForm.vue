<script>
import objectFormMixin from "../../../mixins/objectFormMixin";

export default {
  name: "ObjectForm",
  mixins: [objectFormMixin],
};
</script>

<template>
  <form @submit.stop.prevent="submit">
    <v-form v-model="valid">
      <v-container>
        <v-row align="end">
          <v-col
            cols="12"
            :sm="field.cols || (field.title ? 12 : 6)"
            v-for="field in fields"
            :key="field.value"
          >
            <!-- @slot Per field slot. Use #field-value.field to customize individual fields. -->
            <slot
              v-if="!field.title"
              :label="field.text"
              :name="field.value + '.field'"
              :attrs="buildAttrs(itemModel, field)"
              :on="buildOn(dynamicSetter(itemModel, field.value))"
              :is-create="isCreate"
              :item="itemModel"
              :setter="buildExternalSetter(itemModel)"
            >
              <v-text-field
                :label="field.text"
                :disabled="field?.disabled"
                filled
                v-model="itemModel[field.value]"
              ></v-text-field>
            </slot>
            <div v-else class="text-h5 black--text">
              {{ field.text }}
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-form>
  </form>
</template>
