"""Event subscribers keeping the ``workflow_states`` index fresh."""

from Acquisition import aq_base
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from Products.CMFCore.utils import getToolByName
from typing import Any


def reindex_workflow_states(obj: Any, event: Any) -> None:
    """Keep the index fresh for workflows with a state variable of their own.

    Right after this event, ``WorkflowTool._invokeWithNotification`` reindexes
    every index named after one of the chain's workflow variables. When some
    workflow in the chain drives
    :data:`~collective.multiworkflow.utils.workflow.WORKFLOW_STATES` that already covers
    this index, and reindexing anyway would recompute the object's entire
    metadata record a second time — ZCatalog rebuilds every column on a partial
    reindex, not just the ones named in ``idxs``.

    So the handler only acts when nothing else will: for a chain whose
    workflows all keep bespoke state variables, which is what any workflow
    written before this index existed does.

    :param obj: the object that transitioned.
    :param event: the ``IAfterTransitionEvent`` being handled; unused.
    """
    if not hasattr(aq_base(obj), "reindexObject"):
        return

    wftool = getToolByName(obj, "portal_workflow", None)
    if wftool is None:
        return

    # A site that turned workflow-driven cataloging off means it, and this
    # index is not the place to override that decision.
    if not getattr(wftool, "_default_cataloging", True):
        return

    if WORKFLOW_STATES in (wftool.getCatalogVariablesFor(obj) or {}):
        return

    obj.reindexObject(idxs=[WORKFLOW_STATES])
