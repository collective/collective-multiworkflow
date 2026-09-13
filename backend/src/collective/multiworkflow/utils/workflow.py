"""The values held by the ``workflow_states`` catalog index.

One ``KeywordIndex`` describes an object's whole workflow chain, so a site
gains no further indexes as behaviors contribute more workflows. Each entry
reads ``<workflow-id>|<state-id>``, and the entries are in chain order — the
workflow configured for the type, the one driving ``review_state``, is always
first.

The same name is also the ``state_variable`` an additional workflow should
adopt, and that is not cosmetic. ``WorkflowTool._reindexWorkflowVariables``
reindexes exactly the indexes named after the chain's workflow variables, so a
workflow using this name keeps the index fresh with no help from us;
:func:`~collective.multiworkflow.subscribers.reindex.reindex_workflow_states`
covers the ones that keep a state variable of their own. Sharing the name
across workflows is safe because DCWorkflow keys its status records by workflow
id, not by variable name.
"""

from collective.multiworkflow.api import get_states
from plone.dexterity.content import DexterityContent


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


def formatted_workflow_states(obj: DexterityContent) -> tuple[str, ...]:
    """Describe the object's state in every workflow of its chain.

    :param obj: the object to describe.
    :returns: ``<workflow-id>|<state-id>`` for each workflow of the chain, in
        chain order; empty for an object with no workflow at all.
    """
    return tuple(
        format_state(workflow_id, state)
        for workflow_id, state in get_states(obj).items()
    )
