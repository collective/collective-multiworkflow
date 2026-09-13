"""Tests for the ``plone.exportimport`` patch.

The patch exists because importing an object's workflow history restores its
state without transitioning, leaving every workflow variable but
``review_state`` stale in the catalog. See
``collective.multiworkflow.exportimport``.

The values below are what this package's own example content carries, and are
the shape of the bug: the publication state is correct with or without the
patch, and only the additional workflow's entry and role mappings move.
"""

from typing import Any


#: State the imported example item is in, in each workflow of its chain.
IMPORTED_STATES = {
    "simple_publication_workflow": "published",
    "foundation_member_workflow": "active",
}

#: What the index held before the patch: the initial state the object was
#: catalogued in, not the one the import gave it.
STALE_MEMBERSHIP_STATE = "pending"

#: The one permission the example membership workflow manages.
MANAGE_MEMBERSHIP = "collective.multiworkflow: Manage membership"

#: Roles the membership workflow grants it in ``active``, the imported state.
ACTIVE_ROLES = {"Manager", "Site Administrator", "Owner"}

#: Roles it grants in ``pending``, the initial state, which is what the object
#: keeps without the patch.
PENDING_ROLES = {"Manager", "Site Administrator", "Reviewer"}


def roles_with(obj: Any, permission: str) -> set[str]:
    """Return the roles an object's own role mappings grant a permission.

    :param obj: the object to inspect.
    :param permission: the permission's title.
    :returns: the roles selected for it on the object itself.
    """
    return {
        role["name"] for role in obj.rolesOfPermission(permission) if role["selected"]
    }
