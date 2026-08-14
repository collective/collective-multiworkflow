"""The workflow chain adapter.

Registered for :class:`~collective.multiworkflow.interfaces.
IAdditionalWorkflows` and the workflow tool, making it more specific than
Plone's default chain adapter, which is registered for ``Interface``. It never
replaces the chain configured for a type — it only appends.
"""

from . import logger
from .declaration import collect_contributions
from .interfaces import IAdditionalWorkflows
from plone.base.interfaces import IWorkflowChain
from Products.CMFCore.interfaces import IWorkflowTool
from Products.CMFPlone.workflow import ToolWorkflowChain
from typing import Any
from zope.component import adapter
from zope.interface import implementer


# type-var: zope's stubs type @implementer for classes only, but declaring a
# *function* factory is the pattern Plone uses for ToolWorkflowChain itself.
@adapter(IAdditionalWorkflows, IWorkflowTool)  # type: ignore[type-var]
@implementer(IWorkflowChain)
def additional_workflows_chain(context: Any, tool: Any) -> tuple[str, ...]:
    """Append contributed workflows to the chain configured for the type.

    The base chain is read by calling Plone's default adapter *function*
    directly. That function resolves the chain from the tool's own
    ``_chains_by_type`` mapping rather than through ``getChainFor``, so this
    call cannot re-enter adapter lookup and no recursion guard is needed.

    A contributed id that no workflow in the tool answers to is logged and
    skipped: a bad declaration must never break chain lookup, because a failure
    here would make the object unusable rather than merely misconfigured.

    :param context: the content object providing a participating marker.
    :param tool: the ``portal_workflow`` tool.
    :returns: the base chain followed by the contributed workflows, in order
        and deduplicated.
    """
    chain: list[str] = list(ToolWorkflowChain(context, tool))

    for workflow_id in collect_contributions(context):
        if workflow_id in chain:
            continue
        if tool.getWorkflowById(workflow_id) is None:
            logger.warning(
                "Workflow %r contributed to %r does not exist in "
                "portal_workflow; skipping it.",
                workflow_id,
                "/".join(context.getPhysicalPath())
                if hasattr(context, "getPhysicalPath")
                else context,
            )
            continue
        chain.append(workflow_id)

    return tuple(chain)
