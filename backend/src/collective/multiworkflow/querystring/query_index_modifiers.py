"""Redirect ``review_state`` collection queries that name a workflow onto the chain
index.

A query is moved only when one of its values is qualified. ``review_state`` is
still a catalog index of its own, maintained by whichever workflow drives each
object's ``review_state``, so a criterion written before this add-on was
installed — carrying a bare ``published`` — is left on it and answers exactly as
it always did. The collection editor offers only qualified values, so a criterion
saved from it targets ``workflow_states`` from then on.
"""

from ..utils.workflow import format_state
from ..utils.workflow import STATE_SEPARATOR
from ..utils.workflow import WORKFLOW_STATES
from collections.abc import Iterator
from plone import api
from plone.app.querystring.interfaces import IParsedQueryIndexModifier
from Products.CMFPlone.WorkflowTool import WorkflowTool
from typing import Any
from zope.interface import implementer


#: The stock catalog index the modifier is registered for.
REVIEW_STATE = "review_state"

#: The keys of a parsed query whose contents are state values.
VALUE_KEYS = ("query", "not")


def qualify(state: str) -> str:
    """Name the workflow a bare state id belongs to.

    Values in the index read ``<workflow-id>|<state-id>``, so a bare ``published``
    matches nothing there. :class:`ReviewStateModifier` needs this only for a query
    mixing bare and qualified values, which it has to move as a whole: the catalog
    intersects the results of different indexes, so splitting the values between
    ``review_state`` and ``workflow_states`` would turn an *any of* into an *all of*.

    So a bare id is read as belonging to the site's default workflow, which is the
    same workflow the index always lists first.

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
    """Move a parsed ``review_state`` query that names a workflow onto
    ``workflow_states``."""

    def __call__(self, value: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Choose the index to query, qualifying bare state ids when moving.

        A query none of whose values is qualified stays on ``review_state``,
        untouched. That index still holds what it held before this add-on was
        installed, so the query answers for every type, whichever workflow drives
        its ``review_state``. Qualifying it with the default workflow instead would
        silently drop the types configured with another one.

        A query with a qualified value moves to ``workflow_states``. Every key but
        the value-carrying ones is passed on untouched, and that matters more than
        it looks: ``plone.app.querystring`` parses the *all of* operation to
        ``{"query": [...], "operator": "and"}`` and *excludes* to
        ``{"not": [...]}``. Rebuilding the dict from ``query`` alone would drop the
        operator — silently turning an AND into a KeywordIndex's default OR — and
        would turn an exclusion into an empty query.

        :param value: the parsed query for the ``review_state`` index.
        :returns: the index to query, and the query to use.
        """
        if not any(STATE_SEPARATOR in state for state in self._states(value)):
            return (REVIEW_STATE, value)

        modified = dict(value)
        for key in VALUE_KEYS:
            if key in modified:
                modified[key] = self._qualified(modified[key])
        return (WORKFLOW_STATES, modified)

    def _states(self, value: dict[str, Any]) -> Iterator[str]:
        """Yield every state id a parsed query carries.

        :param value: the parsed query for the ``review_state`` index.
        :returns: the string values of its value-carrying keys, whether each key
            holds a lone string or a sequence of them.
        """
        for key in VALUE_KEYS:
            item = value.get(key)
            if isinstance(item, str):
                yield item
            elif isinstance(item, list | tuple):
                yield from (state for state in item if isinstance(state, str))

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
