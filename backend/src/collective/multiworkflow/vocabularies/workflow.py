"""Vocabulary for workflow states duration range filtering."""

from ..utils.workflow import format_state
from plone import api
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFPlone.WorkflowTool import WorkflowTool
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


def _get_all_workflow_states(wtool: WorkflowTool) -> list[tuple[str, str]]:
    """Get all workflow states from the portal_workflow tool.

    :param wtool: The portal_workflow tool.
    :returns: List of tuples with state value and title.
    """
    states: list[tuple[str, str]] = []
    workflow_ids = wtool.listWorkflows()
    for workflow_id in workflow_ids:
        workflow = wtool.getWorkflowById(workflow_id)
        if workflow is not None:
            for state in workflow.states.values():
                state_key = format_state(workflow_id, state.id)
                state_title = f"{workflow.title}: {state.title}"
                states.append((state_key, state_title))

    return states


@implementer(IVocabularyFactory)
class WorkflowStatesVocabulary:
    """Every state of every workflow, keyed as the index holds them.

    A class rather than a ``@provider``-decorated function because
    ``zope.interface``'s stubs type that decorator for classes only; the
    module-level instance below keeps the ZCML registration unchanged.
    """

    def __call__(self, context: PortalContent) -> SimpleVocabulary:
        """Build a vocabulary with all workflow states.

        :param context: The current content object (unused, required by
            factory).
        :returns: Vocabulary with one term per workflow state.
        """
        # The tool is typed as the interface rather than the implementation.
        wtool: WorkflowTool = api.portal.get_tool("portal_workflow")  # type: ignore[assignment]
        items = _get_all_workflow_states(wtool)
        terms = [
            SimpleTerm(value=value, token=value, title=title) for value, title in items
        ]
        return SimpleVocabulary(terms)


#: The name ``configure.zcml`` registers as the vocabulary utility.
workflow_states = WorkflowStatesVocabulary()
