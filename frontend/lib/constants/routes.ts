/**
 * Every internal path in one place.
 *
 * Components link through these helpers rather than writing string literals,
 * so a route rename is a single edit and a typo is a type error.
 */

export const routes = {
  home: "/",
  about: "/about",
  contact: "/contact",

  // Curated collections: for sale, monthly rent and hotel stays.
  buy: "/buy",
  rent: "/rent",
  stay: "/stay",

  properties: "/properties",
  property: (slug: string) => `/properties/${slug}`,

  developments: "/developments",
  development: (slug: string) => `/developments/${slug}`,

  login: "/login",
  register: "/register",

  account: {
    root: "/account",
    profile: "/account/profile",
    savedProperties: "/account/saved-properties",
    savedSearches: "/account/saved-searches",
    requests: "/account/requests",
    subscription: "/account/subscription",
    listProperty: "/account/list-property",
  },

  dashboard: {
    root: "/dashboard",
    properties: "/dashboard/properties",
    newProperty: "/dashboard/properties/new",
    property: (id: string) => `/dashboard/properties/${id}`,
    developments: "/dashboard/developments",
    leads: "/dashboard/leads",
    lead: (id: string) => `/dashboard/leads/${id}`,
    users: "/dashboard/users",
    roles: "/dashboard/roles",
    subscriptions: "/dashboard/subscriptions",
    analytics: "/dashboard/analytics",
  },
} as const;
