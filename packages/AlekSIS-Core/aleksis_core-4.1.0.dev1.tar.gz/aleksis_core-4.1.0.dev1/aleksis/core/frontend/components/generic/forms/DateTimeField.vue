<script setup>
import DateField from "./DateField.vue";
import TimeField from "./TimeField.vue";
</script>

<template>
  <div>
    <v-row>
      <v-col class="py-0">
        <div>{{ $attrs.label }}</div>
      </v-col>
    </v-row>
    <v-row>
      <v-col :cols="hideTime ? 12 : 7">
        <date-field
          v-model="date"
          v-bind="{ ...$attrs }"
          :label="$t('forms.date_time.date')"
          :min="minDate"
          :max="maxDate"
        />
      </v-col>
      <v-col cols="5" v-if="!hideTime">
        <time-field
          v-model="time"
          v-bind="{ ...$attrs }"
          :label="$t('forms.date_time.time')"
          :min="minTime"
          :max="maxTime"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { DateTime } from "luxon";

export default {
  name: "DateTimeField",
  data() {
    return {
      innerDateTime: this.value,
    };
  },
  props: {
    value: {
      type: String,
      required: false,
      default: undefined,
    },
    min: {
      type: String,
      required: false,
      default: undefined,
    },
    max: {
      type: String,
      required: false,
      default: undefined,
    },
    hideTime: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  computed: {
    dateTime: {
      get() {
        if (this.innerDateTime) {
          return this.$parseISODate(this.innerDateTime);
        }
        return undefined;
      },
      set(value) {
        this.innerDateTime = value;
        this.$emit("input", value);
      },
    },
    date: {
      get() {
        if (this.dateTime) {
          return this.dateTime.toISODate();
        }
        return undefined;
      },
      set(value) {
        let newDateTime = this.dateTime;
        const date = DateTime.fromISO(value);

        newDateTime = newDateTime.set({
          year: date.year,
          month: date.month,
          day: date.day,
        });

        this.dateTime = newDateTime.toISO();
      },
    },
    time: {
      get() {
        if (this.dateTime) {
          return this.dateTime.toFormat("HH:mm");
        }
        return undefined;
      },
      set(value) {
        let newDateTime = this.dateTime;

        const time = DateTime.fromISO(value);

        newDateTime = newDateTime.set({ hour: time.hour, minute: time.minute });

        this.dateTime = newDateTime.toISO();
      },
    },
    minDT() {
      return this.$parseISODate(this.min);
    },
    minDate() {
      return this.minDT.toISODate();
    },
    minTime() {
      if (this.dateTime && this.dateTime.hasSame(this.minDT, "day")) {
        return this.minDT.toFormat("HH:mm");
      } else {
        return undefined;
      }
    },
    maxDT() {
      return this.$parseISODate(this.max);
    },
    maxDate() {
      return this.maxDT.toISODate();
    },
    maxTime() {
      if (this.dateTime && this.dateTime.hasSame(this.maxDT, "day")) {
        return this.maxDT.toFormat("HH:mm");
      } else {
        return undefined;
      }
    },
  },
  watch: {
    value(newValue) {
      this.innerDateTime = newValue;
    },
  },
};
</script>

<style scoped></style>
