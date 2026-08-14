"""``@workflow`` serialization for content with additional workflows.

Extends `plone.restapi`'s expandable element rather than replacing it. The
payload gains a ``chain`` key describing every workflow in the object's chain,
and the top-level ``transitions`` list is narrowed to the primary workflow so
existing clients keep seeing publication transitions only.
"""

from ..api import owning_workflow
from ..interfaces import IAdditionalWorkflows
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services.workflow.info import WorkflowInfo
from Products.CMFCore.utils import getToolByName
from typing import Any
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


#: Variable every stock Plone workflow uses to record its history.
REVIEW_HISTORY = "review_history"


@implementer(IExpandableElement)
@adapter(IAdditionalWorkflows, Interface)
class WorkflowChainInfo(WorkflowInfo):
    """Serialize every workflow in the chain, not just the effective one."""

    def __call__(self, expand: bool = False) -> dict:
        """Return the ``@workflow`` payload for this object.

        :param expand: whether to include the full payload, as opposed to the
            bare ``@id`` used when listing expandable elements.
        :returns: the standard payload, plus a ``chain`` key, and with
            ``transitions`` narrowed to the primary workflow.
        """
        result = super().__call__(expand=expand)
        if not expand:
            return result

        payload = result["workflow"]
        chain = self._serialize_chain()
        payload["chain"] = chain

        if chain:
            # The primary workflow is the first entry: the chain adapter only
            # ever appends, so the type's configured chain always leads.
            payload["transitions"] = chain[0]["transitions"]

        return result

    def _serialize_chain(self) -> list[dict]:
        """Describe each workflow applying to this object.

        :returns: one entry per workflow, in chain order.
        """
        wftool = getToolByName(self.context, "portal_workflow")
        workflows = wftool.getWorkflowsFor(self.context) or []
        transitions = self._transitions_by_workflow(wftool)

        return [
            {
                "workflow_id": workflow.getId(),
                "title": self.context.translate(workflow.title),
                "state_variable": workflow.state_var,
                "state": self._state(wftool, workflow),
                "transitions": transitions.get(workflow.getId(), []),
                "history": self._history(wftool, workflow),
            }
            for workflow in workflows
        ]

    def _state(self, wftool: Any, workflow: Any) -> dict:
        """Return the object's state in one workflow.

        The title comes from the workflow's own state definition rather than
        from ``getTitleForStateOnType``, which resolves through the *type's*
        configured chain and therefore cannot see a contributed workflow.

        :param wftool: the ``portal_workflow`` tool.
        :param workflow: the workflow definition to read.
        :returns: mapping with the state ``id`` and its translated ``title``.
        """
        state_id = wftool.getInfoFor(
            self.context, workflow.state_var, wf_id=workflow.getId()
        )
        state = workflow.states.get(state_id)
        title = state.title if state is not None and state.title else state_id
        return {"id": state_id, "title": self.context.translate(title)}

    def _history(self, wftool: Any, workflow: Any) -> list:
        """Return the object's history in one workflow.

        A workflow that records no history yields an empty list rather than
        raising: ``DCWorkflowDefinition.getInfoFor`` looks the variable up in
        ``self.variables`` and would raise ``KeyError`` for a workflow that
        never declared it.

        The explicit default matters for the same reason: ``review_history``
        carries an info guard, and a read the guard denies raises
        ``WorkflowException`` unless a default is supplied.

        :param wftool: the ``portal_workflow`` tool.
        :param workflow: the workflow definition to read.
        :returns: the workflow's history entries, JSON-compatible.
        """
        if not workflow.isInfoSupported(self.context, REVIEW_HISTORY):
            return []
        history = wftool.getInfoFor(
            self.context, REVIEW_HISTORY, [], wf_id=workflow.getId()
        )
        return json_compatible(history or [])

    def _transitions_by_workflow(self, wftool: Any) -> dict[str, list]:
        """Group the object's available transitions by owning workflow.

        Ownership comes from :func:`collective.multiworkflow.api.
        owning_workflow`, which attributes a transition id defined by more than
        one workflow to the first in chain order — mirroring how
        ``doActionFor`` routes it.

        :param wftool: the ``portal_workflow`` tool.
        :returns: mapping of workflow id to its serialized transitions.
        """
        owner = owning_workflow(self.context)

        grouped: dict[str, list] = {}
        for action in wftool.listActionInfos(object=self.context):
            if action["category"] != "workflow":
                continue
            workflow_id = owner.get(action["id"])
            if workflow_id is None:
                continue
            title = action["title"]
            if isinstance(title, bytes):
                title = title.decode("utf8")
            grouped.setdefault(workflow_id, []).append({
                "@id": f"{self.context.absolute_url()}/@workflow/{action['id']}",
                "title": self.context.translate(title),
            })
        return grouped
