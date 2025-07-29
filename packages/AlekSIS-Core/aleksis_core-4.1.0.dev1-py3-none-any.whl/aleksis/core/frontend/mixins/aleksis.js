/**
 * Mixin with utilities for AlekSIS view components.
 */
import { DateTime } from "luxon";

import errorCodes from "../errorCodes";

const aleksisMixin = {
  data: () => {
    return {
      $_aleksis_safeTrackedEvents: new Array(),
    };
  },
  computed: {
    $hash() {
      return this.$route?.hash ? this.$route.hash.substring(1) : "";
    },
  },
  methods: {
    safeAddEventListener(target, event, handler) {
      console.debug("Safely adding handler for %s on %o", event, target);
      target.addEventListener(event, handler);
      // Add to tracker so we can unregister the handler later
      this.$data.$_aleksis_safeTrackedEvents.push({
        target: target,
        event: event,
        handler: handler,
      });
    },
    $toast(message, state, timeout) {
      this.$root.snackbarItems.push({
        id: crypto.randomUUID(),
        timeout: timeout || 5000,
        message: message,
        color: state || "error",
      });
    },
    $toastError(message, timeout) {
      this.$toast(
        message || this.$t("generic_messages.error"),
        "error",
        timeout,
      );
    },
    $toastSuccess(message, timeout) {
      this.$toast(
        message || this.$t("generic_messages.success"),
        "success",
        timeout,
      );
    },
    $toastInfo(message, timeout) {
      this.$toast(message, "info", timeout);
    },
    $toastWarning(message, timeout) {
      this.$toast(message, "warning", timeout);
    },
    $parseISODate(value) {
      return DateTime.fromISO(value);
    },
    /**
     * Convert a luxon DateTime object to an ISO representation in UTC
     * @param {DateTime} dateTime DateTime object to convert
     * @return {String} ISO string
     */
    $toUTCISO(dateTime) {
      return dateTime.setZone("utc").toISO();
    },
    /**
     * Generic error handler
     * Logs to console, emits an error event &
     * posts a suitable message to the snackbar
     */
    handleMutationError({ graphQLErrors, networkError }) {
      if (graphQLErrors) {
        for (let err of graphQLErrors) {
          console.error(
            "GraphQL error in mutation",
            err.path.join("."),
            ":",
            err.message,
          );
          if (typeof err.message == "string") {
            this.handleError(err.message, errorCodes.graphQlErrorMutation);
          } else if (err.message instanceof Object) {
            // This is for Django's validation mechanism

            if ("fieldErrors" in this) {
              this.fieldErrors = err.message;
            }

            // If field errors are not handled by this component, show them as error message
            let message = "";

            for (const [key, value] of Object.entries(err.message)) {
              if (key === "__all__") {
                message += `${value}<br/>`;
              } else {
                message += `${key}: ${value}<br/>`;
              }
            }
            this.handleError(
              message,
              errorCodes.graphQlErrorMutationValidation,
            );
          }
        }
      }
      if (networkError) {
        console.error("GraphQL network error", networkError);
        this.handleError(
          this.$t("network_errors.snackbar_error_message"),
          errorCodes.networkErrorMutation,
        );
      }
    },
    handleError(error, errorCode) {
      console.error(`[${errorCode}]`, error);
      /**
       * Emits an error
       */
      this.$emit("error", error, errorCode);
      let message = "";
      if (typeof error == "string") {
        // error is a translation key or simply a string
        message = error;
      } else if (
        typeof error == "object" &&
        error.message &&
        typeof error.message == "string"
      ) {
        // error object has a message string
        message = error.message;
      }
      this.$toastError(
        `<div>${message}</div> <small>${this.$t("error_code", {
          errorCode,
        })}</small>`,
      );
    },
    /**
     * Lookup nested key
     * Keys are either an array of string keys or one string with . seperated keys.
     *
     * @returns The value of the nested key
     */
    getKeysRecursive(keys, object) {
      if (Array.isArray(keys)) {
        return keys.reduce((obj, key) => obj[key], object);
      }
      if (typeof keys === "string") {
        return this.getKeysRecursive(keys.split("."), object);
      } else {
        console.error("Expeced array or string got:", keys);
      }
    },
    /**
     * Set nested key
     * Keys are either an array of string keys or one string with . seperated keys.
     *
     * @returns The new value of the nested key
     */
    setKeysRecursive(keys, object, value) {
      if (Array.isArray(keys)) {
        const [first, ...rest] = keys;
        if (rest.length == 0) {
          return (object[first] = value);
        } else {
          return this.setKeysRecursive(rest, object[first], value);
        }
      }
      if (typeof keys === "string") {
        return this.setKeysRecursive(keys.split("."), object, value);
      } else {
        console.error("Expeced array or string got:", keys);
      }
    },
    $backOrElse(fallback = null) {
      if (fallback == null) {
        fallback = this.$router.base || "/";
      }

      if (
        window.history.length <= 2 &&
        this.$route.path === this.$router.history._startLocation
      ) {
        // No history → navigate to fallback
        this.$router.replace(fallback);
        return;
      }

      this.$router.back();
    },
    /**
     * Parse a number from string according to locale.
     *
     * This might seem hacky at first. But hear me out. This might be
     * JavaScript's best number parser since it adds the missing
     * parser to the standardized Intl.NumberFormat.
     *
     * Source: https://stackoverflow.com/a/78941643
     */
    $parseNumber(number) {
      class NumberParser {
        constructor(locale) {
          const format = new Intl.NumberFormat(locale);
          const parts = format.formatToParts(-12345.6);
          const numerals = Array.from({ length: 10 }).map((_, i) =>
            format.format(i),
          );
          const index = new Map(numerals.map((d, i) => [d, i]));
          this._minusSign = new RegExp(
            `[${parts.find((d) => d.type === "minusSign").value}]`,
          );
          this._group = new RegExp(
            `[${parts.find((d) => d.type === "group").value}]`,
            "g",
          );
          this._decimal = new RegExp(
            `[${parts.find((d) => d.type === "decimal").value}]`,
          );
          this._numeral = new RegExp(`[${numerals.join("")}]`, "g");
          this._index = (d) => index.get(d);
        }
        parse(string) {
          const DIRECTION_MARK = /\u061c|\u200e/g;
          return +string
            .trim()
            .replace(DIRECTION_MARK, "")
            .replace(this._group, "")
            .replace(this._decimal, ".")
            .replace(this._numeral, this._index)
            .replace(this._minusSign, "-");
        }
      }

      return new NumberParser().parse(number);
    },
  },
  mounted() {
    this.$emit("mounted");
  },
  beforeDestroy() {
    // Unregister all safely added event listeners as to not leak them
    for (let trackedEvent in this.$data.$_aleksis_safeTrackedEvents) {
      if (trackedEvent.target) {
        console.debug(
          "Removing handler for %s on %o",
          trackedEvent.event,
          trackedEvent.target,
        );
        trackedEvent.target.removeEventListener(
          trackedEvent.event,
          trackedEvent.handler,
        );
      } else {
        console.debug("Target already removed while removing event handler");
      }
    }
  },
};

export default aleksisMixin;
