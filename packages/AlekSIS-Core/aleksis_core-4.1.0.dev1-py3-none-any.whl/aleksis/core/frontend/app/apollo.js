/*
 * Configuration for Apollo provider, client, and caches.
 */

import { ApolloClient } from "@/apollo-boost";

import { persistCache, LocalStorageWrapper } from "@/apollo3-cache-persist";
import {
  InMemoryCache,
  IntrospectionFragmentMatcher,
} from "@/apollo-cache-inmemory";
import createUploadLink from "@/apollo-upload-client/createUploadLink.mjs";

import { gqlSchema } from "aleksisApolloOptions";

import errorCodes from "../errorCodes";

const fragmentMatcher = new IntrospectionFragmentMatcher({
  introspectionQueryResultData: gqlSchema,
});

// Cache for GraphQL query results in memory and persistent across sessions
const cache = new InMemoryCache({ fragmentMatcher });
await persistCache({
  cache: cache,
  storage: new LocalStorageWrapper(window.localStorage),
});

/**
 * Construct the GraphQL endpoint URI.
 *
 * @returns The URI of the GraphQL endpoint on the AlekSIS server
 */
function getGraphqlURL() {
  const settings = JSON.parse(
    document.getElementById("frontend_settings").textContent,
  );
  const base = settings.urls.base || window.location.origin;
  return new URL(settings.urls.graphql, base);
}

/** Upstream Apollo GraphQL client */
const apolloClient = new ApolloClient({
  cache,
  link: createUploadLink({
    uri: getGraphqlURL(),
  }),
});

const apolloOpts = {
  defaultClient: apolloClient,
  defaultOptions: {
    $query: {
      skip: function (vm, queryKey) {
        if (queryKey in vm.$_apollo.queries) {
          // We only want to run this query when background activity is on and we are not reported offline
          return !!(
            vm.$_apollo.queries[queryKey].options.pollInterval &&
            (!vm.$root.backgroundActive || vm.$root.offline)
          );
        }
        return false;
      },
      error: ({ graphQLErrors, networkError }, vm) => {
        if (networkError) {
          // Set app offline globally on network errors
          //  This will cause the offline logic to kick in, starting a ping check or
          //  similar recovery strategies depending on the app/navigator state
          console.error(
            "Network error:",
            networkError.statusCode,
            networkError,
          );
          if (!networkError.statusCode || networkError.statusCode >= 500) {
            console.error(
              "Network error during GraphQL query, setting offline state",
            );
            vm.$root.offline = true;
          }

          vm.$root.maintenance = networkError.statusCode === 503;
        }
        if (graphQLErrors) {
          for (let err of graphQLErrors) {
            if (
              JSON.parse(
                document.getElementById("frontend_settings").textContent,
              ).sentry &&
              JSON.parse(
                document.getElementById("frontend_settings").textContent,
              ).sentry.enabled
            ) {
              vm.$root.$sentry.captureException(err);
            }

            console.error(
              "GraphQL error in query",
              err.path.join("."),
              ":",
              err.message,
            );
          }
          // Add a snackbar on all errors returned by the GraphQL endpoint
          //  If App is offline, don't add snackbar since only the ping query is active
          if (!vm.$root.offline) {
            vm.handleError(
              vm.$t("graphql.snackbar_error_message"),
              errorCodes.graphQlErrorQuery,
            );
          }
        }
      },
      fetchPolicy: "cache-and-network",
    },
  },
};

export default apolloOpts;
