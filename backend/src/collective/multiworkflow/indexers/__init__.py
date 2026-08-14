"""The ``workflow_states`` catalog index.

One ``KeywordIndex`` describes an object's whole workflow chain, so a site
gains no further indexes as behaviors contribute more workflows. Each entry
reads ``<workflow-id>|<state-id>``, and the entries are in chain order — the
workflow configured for the type, the one driving ``review_state``, is always
first.

The same name is also the ``state_variable`` an additional workflow should
adopt, and that is not cosmetic. ``WorkflowTool._reindexWorkflowVariables``
reindexes exactly the indexes named after the chain's workflow variables, so a
workflow using this name keeps the index fresh with no help from us;
:func:`reindex_workflow_states` covers the ones that keep a state variable of
their own. Sharing the name across workflows is safe because DCWorkflow keys
its status records by workflow id, not by variable name.

What the catalog stores is always :func:`workflow_states` and never the
workflow variable that happens to share its name: ``plone.indexer``'s wrapper
consults ``IIndexer`` adapters *before* workflow variables.
"""

from ..api import get_states
from Acquisition import aq_base
from plone.indexer.decorator import indexer
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.utils import getToolByName
from typing import Any


#: Name of the index, of the metadata column, and the ``state_variable`` an
#: additional workflow should adopt.
WORKFLOW_STATES = "workflow_states"

#: Separates the workflow id from the state id within one indexed value.
#: Neither id can contain it — both are Zope ids.
STATE_SEPARATOR = "|"


def format_state(workflow_id: str, state_id: str) -> str:
    """Build one indexed value out of a workflow id and a state id.

    :param workflow_id: id of the workflow the state belongs to.
    :param state_id: id of the state that workflow is in.
    :returns: the value as the catalog holds it.
    """
    return f"{workflow_id}{STATE_SEPARATOR}{state_id}"


def parse_state(value: str) -> tuple[str, str]:
    """Split one indexed value back into its workflow id and state id.

    :param value: a value as :func:`format_state` produced it.
    :returns: the workflow id and the state id.
    :raises ValueError: if the value carries no separator.
    """
    workflow_id, separator, state_id = value.partition(STATE_SEPARATOR)
    if not separator:
        raise ValueError(f"{value!r} is not a {WORKFLOW_STATES} value.")
    return workflow_id, state_id


@indexer(IContentish)
def workflow_states(obj: Any) -> tuple[str, ...]:
    """Index every workflow in the object's chain, in chain order.

    Registered for all content rather than for participating content alone, so
    that the first entry is the object's ``review_state`` whether or not
    anything was contributed to it — callers can rely on entry zero without
    first asking whether the object participates.

    :param obj: the object being catalogued.
    :returns: ``<workflow-id>|<state-id>`` for each workflow of the chain;
        empty for an object with no workflow at all.
    """
    return tuple(
        format_state(workflow_id, state)
        for workflow_id, state in get_states(obj).items()
    )


def reindex_workflow_states(obj: Any, event: Any) -> None:
    """Keep the index fresh for workflows with a state variable of their own.

    Right after this event, ``WorkflowTool._invokeWithNotification`` reindexes
    every index named after one of the chain's workflow variables. When some
    workflow in the chain drives :data:`WORKFLOW_STATES` that already covers
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
