// Configuration for Vite bundling
//
// This config is somewhat elaborate, because it needs to dynamically address
// the several environments where it is used. The AlekSIS frontend bundle is
// always created as a custom asset for a given Django deployment, in order
// to allow for dynamic addition of frontend code from AlekSIS apps.
//
// It is therefore also placed inside the Python package structure, so it
// will be installed into the target system/image by poetry.
//
// Hence, the main scenarios are:
//
//  * called directly from the source tree of AlekSIS-Core, with
//    cache dir (and thus node_module) in ./cache
//  * called from basically anywhere, with the cace dir also anywhere
//
// Vite must always be called through the `aleksis-admin vite` wrapper, which
// generates a JSON file with some hints in the cache directory, so we can
// make Vite find all the puzzle pieces.

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const process = require("process");

import { defineConfig, searchForWorkspaceRoot } from "vite";
import vue from "@vitejs/plugin-vue2";
import { nodeResolve } from "@rollup/plugin-node-resolve";
import graphql from "@rollup/plugin-graphql";
import virtual from "@rollup/plugin-virtual";
import { VitePWA } from "vite-plugin-pwa";
import topLevelAwait from "vite-plugin-top-level-await";
import browserslistToEsbuild from "browserslist-to-esbuild";
const license = require("rollup-plugin-license");
import SupportedBrowsers from "vite-plugin-browserslist-useragent";
import legacy from "@vitejs/plugin-legacy";

// Read the hints writen by `aleksis-admin vite`
const django_values = JSON.parse(fs.readFileSync("./django-vite-values.json"));

// Browsers supported by us
const browsersList = [
  "defaults and supports es6-module",
  ">0.2% in de and supports es6-module",
];

/**
 * Generate code to import messages from a single AlekSIS app.
 */
function generateMessageImportCode(assetDir, name, importAppName) {
  let code = "";
  let messagesPath = assetDir + "/messages/";
  code += `appMessages["${name}"] = {};`;
  const files = fs.readdirSync(messagesPath);
  for (file of files) {
    let lang = file.split(".")[0];
    code += `import ${importAppName}Messages_${lang} from '${
      messagesPath + file
    }';\n`;
    code += `appMessages["${name}"]["${lang}"] = ${importAppName}Messages_${lang};\n`;
  }
  return code;
}

/**
 * Generate code to import all components from a specified directory of a single AlekSIS app.
 */
function generateComponentsImportCode(
  assetDir,
  componentsDir,
  name,
  exportName,
) {
  let code = "";
  let componentsPath = assetDir + "/components" + componentsDir;
  if (fs.existsSync(componentsPath)) {
    const files = fs.readdirSync(componentsPath);
    for (file of files) {
      let componentName = file.split(".")[0];
      code += `import ${componentName} from '${componentsPath + file}';\n`;
      code += `${exportName}["${componentName.toLowerCase()}"] = ${componentName};\n`;
    }
  }
  return code;
}

/**
 * Generate a virtual module that helps the AlekSIS-Core frontend code import other apps.
 *
 * App code locations are discovered by the `aleksis-admin` vite wrapper and passed
 * in the django_values hints.
 */
function generateAppImporter(appDetails) {
  let code = "let appObjects = {};\n";
  code += "let appMessages = {};\n";
  code += "let calendarFeedDetailComponents = {};\n";
  code += "let calendarFeedEventBarComponents = {};\n";
  code += "let collections = [];\n";
  code += "let collectionItemsS = [];\n";

  code += `
  function transformCollection(appName) {
    return (collection, index) => ({
      ...collection,
      name: appName + collection.name.charAt(0).toUpperCase() + collection.name.substring(1),
      type: collection.type,
      order: collection.order ?? index,
      items: collection.items || [],
    });
  }
  `;

  for (const [appPackage, appMeta] of Object.entries(appDetails)) {
    let indexPath = appMeta.assetDir + "/index.js";
    let importAppName =
      appMeta.name.charAt(0).toUpperCase() + appMeta.name.substring(1);

    code += `console.debug("Importing AlekSIS app entrypoint for ${appPackage}");\n`;
    code += `const ${importAppName} = await import("${indexPath}");\n`;
    code += `appObjects["${appMeta.name}"] = ${importAppName}.default;\n`;

    if (appMeta.hasMessages) {
      code += generateMessageImportCode(
        appMeta.assetDir,
        appMeta.name,
        importAppName,
      );
    }

    // Include calendar feed detail components from all apps
    code += generateComponentsImportCode(
      appMeta.assetDir,
      "/calendar_feeds/details/",
      appMeta.name,
      "calendarFeedDetailComponents",
    );

    // Include calendar feed event bar components from all apps
    code += generateComponentsImportCode(
      appMeta.assetDir,
      "/calendar_feeds/event_bar/",
      appMeta.name,
      "calendarFeedEventBarComponents",
    );

    code += `
    const {
      collections: ${importAppName}Collections = [],
      collectionItems: ${importAppName}CollectionItems = {},
    } = ${importAppName};\n

    collections.push(...(${importAppName}Collections.map(transformCollection("${appMeta.name}"))));\n
    collectionItemsS.push(${importAppName}CollectionItems);\n
    `;
  }

  code += `
    const {
      collections: coreCollections = [],
      collectionItems: coreCollectionItems = {},
    } = await import("${django_values.coreAssetDir}/collections.js");\n;

    collections.push(...(coreCollections.map(transformCollection("core"))));\n
    collectionItemsS.push(coreCollectionItems);\n

    collectionItemsS.forEach(collectionItems =>
       Object.entries(collectionItems).forEach(([collectionName, items]) =>
           collections.find(c => c.name === collectionName)?.items.push(...items)
       )
    );\n

    collections = Object.fromEntries(collections.map(c => [c.name, c]));\n
  `;

  // Include core messages
  code += generateMessageImportCode(django_values.coreAssetDir, "core", "Core");

  // Include core calendar feed detail components
  code += generateComponentsImportCode(
    django_values.coreAssetDir,
    "/calendar_feeds/details/",
    "core",
    "calendarFeedDetailComponents",
  );

  // Include core calendar feed event bar components
  code += generateComponentsImportCode(
    django_values.coreAssetDir,
    "/calendar_feeds/event_bar/",
    "core",
    "calendarFeedEventBarComponents",
  );

  code += "export default appObjects;\n";
  code += `
    export {
      appObjects,
      appMessages,
      calendarFeedDetailComponents,
      calendarFeedEventBarComponents,
      collections,
    };\n`;
  console.log(code);
  return code;
}

export default defineConfig({
  // root must always be the base directory of the AlekSIS-Core source tree
  //  Changing this will mangle the manifest key of the entrypoint!
  root: django_values.baseDir,
  // Base URL needs to mimic the /static/ URL in Django
  base: django_values.static_url,
  build: {
    outDir: path.resolve("./vite_bundles/"),
    manifest: true,
    target: browserslistToEsbuild(browsersList),
    rollupOptions: {
      input: django_values.coreAssetDir + "/index.js",
      output: {
        manualChunks(id) {
          // Split big libraries into own chunks
          if (id.includes("node_modules/vue")) {
            return "vue";
          } else if (id.includes("node_modules/apollo")) {
            return "apollo";
          } else if (id.includes("node_modules/graphql")) {
            return "graphql";
          } else if (id.includes("node_modules/@sentry")) {
            return "sentry";
          } else if (id.includes("node_modules")) {
            // Fallback for all other libraries
            return "vendor";
          }

          // Split each AlekSIS app in its own chunk
          for (const [appPackage, ad] of Object.entries(
            django_values.appDetails,
          )) {
            if (id.includes(ad.assetDir + "/index.js")) {
              return appPackage;
            }
          }
        },
      },
    },
  },
  server: {
    strictPort: true,
    port: django_values.serverPort,
    origin: `http://localhost:${django_values.serverPort}`,
    watch: {
      ignored: [
        "**/*.py",
        "**/__pycache__/**",
        "**/*.mo",
        "**/.venv/**",
        "**/.tox/**",
        "**/static/**",
        "**/assets/**",
      ],
    },
    fs: {
      allow: [
        searchForWorkspaceRoot(path.resolve(django_values.baseDir)),
        ...Object.values(django_values.appDetails).map(
          (details) => details.assetDir,
        ),
      ],
    },
  },
  plugins: [
    virtual({
      // Will be used in AlekSIS-Core frontend code to import aps
      aleksisAppImporter: generateAppImporter(django_values.appDetails),
    }),
    vue(),
    nodeResolve({ modulePaths: [path.resolve(django_values.node_modules)] }),
    graphql(),
    topLevelAwait(),
    license({
      // A package.json will be written here by `aleksis-admin vite`
      cwd: path.resolve(django_values.cacheDir),
      banner: {
        commentStyle: "ignored",
        content: `Frontend bundle for AlekSIS\nSee ./vendor.LICENSE.txt for copyright information.`,
      },
      thirdParty: {
        allow: {
          test: "MIT OR Apache-2.0 OR 0BSD OR BSD-3-Clause",
          failOnUnlicensed: true,
          failOnViolation: true,
        },
        output: {
          file: path.resolve(
            django_values.cacheDir + "/vite_bundles/assets/vendor.LICENSE.txt",
          ),
        },
      },
    }),
    SupportedBrowsers({
      browsers: browsersList,
      ignoreMinor: true,
      allowHigherVersions: true,
    }),
    legacy({
      targets: browsersList,
      modernPolyfills: true,
    }),
    VitePWA({
      injectRegister: "null",
      devOptions: {
        enabled: true,
      },
      scope: "/",
      base: "/",
      workbox: {
        navigateFallback: "/",
        directoryIndex: null,
        navigateFallbackAllowlist: [
          new RegExp(
            "^/(?!(django|admin|graphql|__icons__|oauth/authorize|o))[^.]*$",
          ),
        ],
        additionalManifestEntries: [
          { url: "/", revision: crypto.randomUUID() },
          { url: "/django/offline/", revision: crypto.randomUUID() },
        ],
        inlineWorkboxRuntime: true,
        modifyURLPrefix: {
          "": "/static/",
        },
        globPatterns: ["**/*.{js,css,eot,woff,woff2,ttf}"],
        runtimeCaching: [
          {
            urlPattern: new RegExp(
              "^/(?!(django|admin|graphql|__icons__|oauth/authorize|o))[^.]*$",
            ),
            handler: "CacheFirst",
          },
          {
            urlPattern: new RegExp("/django/.*"),
            handler: "NetworkFirst",
            options: {
              cacheName: "aleksis-legacy-cache",
              networkTimeoutSeconds: 5,
              expiration: {
                maxAgeSeconds: 60 * 60 * 24,
              },
              precacheFallback: {
                fallbackURL: "/django/offline/",
              },
              cacheableResponse: {
                headers: {
                  "PWA-Is-Cacheable": "true",
                },
              },
              plugins: [
                {
                  fetchDidSucceed: async ({ request, response }) => {
                    if (response.status < 500) {
                      return response;
                    }
                    throw new Error(
                      `${response.status} ${response.statusText}`,
                    );
                  },
                },
              ],
            },
          },
          {
            urlPattern: ({ request, sameOrigin }) => {
              return sameOrigin && request.destination === "image";
            },
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "aleksis-image-cache",
              expiration: {
                maxAgeSeconds: 60 * 60 * 24,
              },
            },
          },
          {
            urlPattern: ({ request, sameOrigin }) => {
              return sameOrigin && request.destination === "style";
            },
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "aleksis-style-cache",
              expiration: {
                maxAgeSeconds: 60 * 60 * 24 * 30,
              },
            },
          },
          {
            urlPattern: ({ request, sameOrigin }) => {
              return sameOrigin && request.destination === "script";
            },
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "aleksis-script-cache",
              expiration: {
                maxAgeSeconds: 60 * 60 * 24 * 30,
              },
            },
          },
          {
            urlPattern: ({ request, sameOrigin }) => {
              return sameOrigin && request.destination === "font";
            },
            handler: "CacheFirst",
            options: {
              cacheName: "aleksis-font-cache",
              expiration: {
                maxAgeSeconds: 60 * 60 * 24 * 90,
              },
            },
          },
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(django_values.node_modules),
      vue: path.resolve(django_values.node_modules + "/vue/dist/vue.esm.js"),
      "aleksis.core": django_values.coreAssetDir,
      // Add aliases for every app using their package name
      ...Object.fromEntries(
        Object.entries(django_values.appDetails).map(([name, appMeta]) => [
          name,
          appMeta.assetDir,
        ]),
      ),
    },
  },
});
