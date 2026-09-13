"""Tests for the ``workflow_states`` catalog index.

Shared values for the package live here so test modules and ``conftest`` import
them relatively.

The workflow this package builds keeps a **bespoke** state variable on purpose.
That is the half of the freshness contract CMFCore does not cover — it reindexes
only indexes named after a chain variable — so it is the half that exercises
:func:`collective.multiworkflow.subscribers.reindex.reindex_workflow_states`. The demo
workflow, which adopts the shared variable, covers the other half over in
``tests.demo``.
"""

from collective.multiworkflow.interfaces import IAdditionalWorkflows


AUDIT_WORKFLOW = "audit_workflow"

#: Deliberately *not* the indexed name, so nothing but the subscriber can keep
#: this workflow's entry in the index up to date.
AUDIT_STATE_VAR = "audit_state"


class IAudited(IAdditionalWorkflows):
    """Marker contributing a workflow with a state variable of its own."""
