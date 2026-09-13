"""The ``workflow_states`` catalog indexer.

What the catalog stores is always this indexer's value, never the workflow
variable that may share its name: ``plone.indexer``'s wrapper consults
``IIndexer`` adapters *before* workflow variables. The format of the values is
described in :mod:`collective.multiworkflow.utils.workflow`.
"""

from collective.multiworkflow.utils.workflow import formatted_workflow_states
from plone.dexterity.content import DexterityContent
from plone.indexer.decorator import indexer
from Products.CMFCore.interfaces import IContentish


@indexer(IContentish)
def workflow_states(obj: DexterityContent) -> tuple[str, ...]:
    """Index every workflow in the object's chain, in chain order.

    Registered for all content rather than for participating content alone, so
    that the first entry is the object's ``review_state`` whether or not
    anything was contributed to it — callers can rely on entry zero without
    first asking whether the object participates.

    :param obj: the object being catalogued.
    :returns: ``<workflow-id>|<state-id>`` for each workflow of the chain;
        empty for an object with no workflow at all.
    """
    return formatted_workflow_states(obj)
