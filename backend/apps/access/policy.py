"""Capability vocabulary.

The permission strings the product understands, in one place. Domain apps
reference these constants instead of inventing strings, and instead of asking
whether a user is an agent.
"""

from __future__ import annotations

from typing import Final


class Capability:
    PROPERTY_VIEW_ALL: Final = "properties.view_all"
    PROPERTY_CREATE: Final = "properties.create"
    PROPERTY_EDIT_OWN: Final = "properties.edit_own"
    PROPERTY_EDIT_ANY: Final = "properties.edit_any"
    PROPERTY_PUBLISH: Final = "properties.publish"
    PROPERTY_ARCHIVE: Final = "properties.archive"

    DEVELOPMENT_MANAGE: Final = "developments.manage"
    MEDIA_MANAGE: Final = "media.manage"

    LEAD_VIEW_OWN: Final = "leads.view_own"
    LEAD_VIEW_ALL: Final = "leads.view_all"
    LEAD_ASSIGN: Final = "leads.assign"
    LEAD_RESPOND: Final = "leads.respond"

    USER_MANAGE: Final = "users.manage"
    ROLE_MANAGE: Final = "roles.manage"
    SUBSCRIPTION_MANAGE: Final = "subscriptions.manage"
    AUDIT_VIEW: Final = "audit.view"


#: Seed definitions applied by the `seed_roles` management command.
SYSTEM_ROLE_DEFINITIONS = [
    {
        "code": "client",
        "name": "Client",
        "description": "A registered visitor of the public website.",
        "areas": ["public", "client"],
        "permissions": [],
        "priority": 300,
    },
    {
        "code": "agent",
        "name": "Agent",
        "description": "Sells and manages their own portfolio in the dashboard.",
        "areas": ["public", "client", "dashboard"],
        "permissions": [
            Capability.PROPERTY_CREATE,
            Capability.PROPERTY_EDIT_OWN,
            Capability.MEDIA_MANAGE,
            Capability.LEAD_VIEW_OWN,
            Capability.LEAD_RESPOND,
        ],
        "priority": 200,
    },
    {
        "code": "staff",
        "name": "Staff",
        "description": "Full internal operation of the platform.",
        "areas": ["public", "client", "dashboard", "internal"],
        "permissions": [
            Capability.PROPERTY_VIEW_ALL,
            Capability.PROPERTY_CREATE,
            Capability.PROPERTY_EDIT_ANY,
            Capability.PROPERTY_PUBLISH,
            Capability.PROPERTY_ARCHIVE,
            Capability.DEVELOPMENT_MANAGE,
            Capability.MEDIA_MANAGE,
            Capability.LEAD_VIEW_ALL,
            Capability.LEAD_ASSIGN,
            Capability.LEAD_RESPOND,
            Capability.USER_MANAGE,
            Capability.ROLE_MANAGE,
            Capability.SUBSCRIPTION_MANAGE,
            Capability.AUDIT_VIEW,
        ],
        "priority": 100,
    },
]

DEFAULT_ROLE_CODE = "client"
