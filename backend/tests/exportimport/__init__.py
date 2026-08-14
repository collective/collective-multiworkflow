"""Tests for the ``plone.exportimport`` patch.

The patch exists because importing an object's workflow history restores its
state without transitioning, leaving every workflow variable but
``review_state`` stale in the catalog. See
``collective.multiworkflow.exportimport``.

The values below are what this package's own example content carries, and are
the shape of the bug: the publication state is correct with or without the
patch, and only the additional workflow's entry moves.
"""

#: State the imported example item is in, in each workflow of its chain.
IMPORTED_STATES = {
    "simple_publication_workflow": "published",
    "foundation_member_workflow": "active",
}

#: What the index held before the patch: the initial state the object was
#: catalogued in, not the one the import gave it.
STALE_MEMBERSHIP_STATE = "pending"
