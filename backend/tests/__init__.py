"""Test suite for collective.multiworkflow.

Each subpackage is a real package: shared values live in its ``__init__``, so
test modules import them relatively and there is no ambiguity between the
``conftest`` modules of sibling directories.

Values every subpackage needs live *here* instead, alongside the fixtures in
this directory's ``conftest``. A subpackage keeps only the vocabulary that is
its own — the workflows it builds programmatically, say, which share a name
across packages but not a shape.
"""

from AccessControl.Permission import Permission
from Products.CMFCore.indexing import processQueue
from typing import Any
from zope.interface import Interface


PUBLICATION_WORKFLOW = "simple_publication_workflow"

#: What ``portal_workflow`` reports for a type nothing has contributed to.
BASE_CHAIN = (PUBLICATION_WORKFLOW,)

#: The participating type: introduced by the demo profile, which the test layer
#: applies, and carrying the example behavior in its own FTI.
MEMBER_PROFILE = {
    "type": "Profile",
    "id": "member-profile",
    "title": "A Member Profile",
}

#: A stock type the demo profile does not touch, for every assertion about
#: content the add-on must leave alone.
PLAIN_DOCUMENT = {
    "type": "Document",
    "id": "plain-doc",
    "title": "A Plain Document",
}


# --- Spike scaffolding -------------------------------------------------------
#
# Modules named ``test_spike_*`` assert how *Plone* behaves, not how this
# package behaves, so they must not route through ``IAdditionalWorkflows`` or
# the real chain adapter. They get their own marker, their own workflows and
# their own hand-rolled adapter, all named ``spike_*`` so that landing them in a
# package that already defines a ``membership_workflow`` cannot silently
# substitute one for the other.


class IExtraWorkflows(Interface):
    """Stand-in for ``IAdditionalWorkflows``, used only by the spikes."""


SPIKE_WORKFLOW = "spike_membership_workflow"
SPIKE_STATE_VAR = "spike_state"

#: Transition id deliberately shared with ``simple_publication_workflow`` so
#: the collision spike can observe how ``doActionFor`` resolves it.
SPIKE_COLLIDING_WORKFLOW = "spike_colliding_workflow"
SPIKE_COLLIDING_STATE_VAR = "spike_collision_state"


def flush_indexing() -> None:
    """Write CMFCore's pending indexing operations to the catalog.

    ``CatalogTool.reindexObject`` does not touch an index directly: it queues
    the object and lets the queue write at transaction boundaries. A test that
    never commits therefore queries a catalog that may be several operations
    behind, and — because a query does not flush the queue either — an
    assertion about an index can pass or fail on how much of the queue happens
    to have drained. Call this before any assertion that reads an index.

    Metadata behaves differently, as observed rather than as reasoned from the
    queue's implementation: a brain can carry the right value while the index
    that should have found it holds nothing. That is precisely why the index
    tests assert on queries and never on brains.
    """
    processQueue()


def roles_for(obj: Any, permission: str) -> tuple[str, ...]:
    """Read the roles a permission is mapped to on one object.

    Reads the mangled attribute ``modifyRolesForPermission`` writes, which is
    what a workflow's role mapping actually sets, rather than going through
    ``rolesOfPermission`` — that one needs the permission to be declared in the
    class's ``__ac_permissions__``.

    :param obj: object to read the mapping from.
    :param permission: title of the permission, as workflows name it.
    :returns: the roles holding the permission, sorted; empty when the object
        acquires the mapping instead of defining it.
    """
    roles = Permission(permission, (), obj).getRoles(default=())
    return tuple(sorted(roles))
