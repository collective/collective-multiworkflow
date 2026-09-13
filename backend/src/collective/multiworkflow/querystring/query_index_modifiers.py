"""Redirect ``review_state`` collection queries onto the chain index."""

from ..utils.workflow import format_state
from ..utils.workflow import STATE_SEPARATOR
from ..utils.workflow import WORKFLOW_STATES
from plone import api
from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from Products.CMFPlone.WorkflowTool import WorkflowTool
from typing import Any
from zope.interface import implementer


#: The keys of a parsed query whose contents are state values.
VALUE_KEYS = ("query", "not")


def qualify(state: str) -> str:
    """Name the workflow a bare state id belongs to.

    Values in the index read ``<workflow-id>|<state-id>``, but a criterion
    written against ``review_state`` — a stored collection predating this
    add-on, or a query built in code — carries a bare ``published``. Left
    alone, such a value matches nothing at all, which reads as "no content in
    that state" rather than as a query that could never have worked.

    So a bare id is read as belonging to the site's default workflow, which is
    the same workflow the index always lists first.

    :param state: a state id, qualified or not.
    :returns: the value as the index holds it; unchanged when it was already
        qualified, or when the site declares no default chain to attribute it
        to.
    """
    if STATE_SEPARATOR in state:
        return state

    # The tool is typed as the interface rather than the implementation.
    wftool: WorkflowTool = api.portal.get_tool("portal_workflow")  # type: ignore[assignment]
    chain = wftool.getDefaultChain()
    if not chain:
        return state
    return format_state(chain[0], state)


@implementer(IParsedQueryIndexModifier)
class ReviewStateModifier:
    """Rewrite a parsed ``review_state`` query to target ``workflow_states``."""

    def __call__(self, value: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Rename the index, qualifying bare state ids on the way through.

        Every key but the value-carrying ones is passed on untouched, and that
        matters more than it looks: ``plone.app.querystring`` parses the *all
        of* operation to ``{"query": [...], "operator": "and"}`` and *excludes*
        to ``{"not": [...]}``. Rebuilding the dict from ``query`` alone would
        drop the operator — silently turning an AND into a KeywordIndex's
        default OR — and would turn an exclusion into an empty query.

        :param value: the parsed query for the ``review_state`` index.
        :returns: the index to query instead, and the query to use.
        """
        modified = dict(value)
        for key in VALUE_KEYS:
            if key in modified:
                modified[key] = self._qualified(modified[key])
        return (WORKFLOW_STATES, modified)

    def _qualified(self, value: Any) -> Any:
        """Qualify one parsed value, whatever shape it arrived in.

        A lone string becomes a one-item list: the index is a KeywordIndex, so
        callers reading the query back get a consistent shape either way.

        :param value: a state id, a sequence of them, or something else
            entirely — a date range, say, which is passed through untouched.
        :returns: the qualified equivalent.
        """
        if isinstance(value, str):
            return [qualify(value)]
        if isinstance(value, list | tuple):
            return [qualify(item) if isinstance(item, str) else item for item in value]
        return value
