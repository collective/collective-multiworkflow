"""Workflow-aware equivalents of the ``plone.api`` workflow helpers.

Every signature is a **pure superset** of what ``plone.api.content`` offers
today: called without ``workflow_id`` these behave exactly as their upstream
counterparts, reading and driving ``review_state``. Passing ``workflow_id``
addresses one specific workflow in the object's chain.
"""

from plone import api as plone_api
from plone.api.exc import InvalidParameterError
from plone.dexterity.content import DexterityContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.WorkflowTool import WorkflowTool
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from typing import Any


_marker = object()


def _tool(obj: Any) -> WorkflowTool:
    """Return the workflow tool for an object.

    :param obj: any content object.
    :returns: the ``portal_workflow`` tool.
    """
    return getToolByName(obj, "portal_workflow")


def _workflow(wftool: WorkflowTool, workflow_id: str) -> DCWorkflowDefinition:
    """Look a workflow up, failing loudly on an unknown id.

    :param wftool: the ``portal_workflow`` tool.
    :param workflow_id: id of the workflow to look up.
    :returns: the workflow definition.
    :raises InvalidParameterError: if no such workflow is registered.
    """
    workflow = wftool.getWorkflowById(workflow_id)
    if workflow is None:
        raise InvalidParameterError(f"Unknown workflow '{workflow_id}'.")
    return workflow


def get_state(
    obj: DexterityContent, default: Any = _marker, workflow_id: str | None = None
) -> str:
    """Get the object's current state, optionally in a specific workflow.

    With no ``workflow_id`` this is ``plone.api.content.get_state``: it returns
    ``review_state``. ``workflow_id`` selects one workflow from the chain and
    returns the value of *that* workflow's state variable.

    :param obj: object to read the state of.
    :param default: returned if the object has no workflow at all.
    :param workflow_id: id of the workflow to read; ``None`` means the
        effective ``review_state``.
    :returns: the current state id.
    :raises InvalidParameterError: if ``workflow_id`` is not registered.
    :raises WorkflowException: if the state cannot be determined.
    """
    wftool = _tool(obj)

    if default is not _marker and not wftool.getWorkflowsFor(obj):
        return default

    if workflow_id is None:
        return wftool.getInfoFor(ob=obj, name="review_state")

    workflow = _workflow(wftool, workflow_id)
    return wftool.getInfoFor(obj, workflow.state_var, wf_id=workflow_id)


def get_states(obj: DexterityContent) -> dict[str, str]:
    """Get the object's state in every workflow of its chain.

    :param obj: object to read the states of.
    :returns: mapping of workflow id to the current state id, in chain order.
    """
    wftool = _tool(obj)
    return {
        workflow.getId(): wftool.getInfoFor(
            obj, workflow.state_var, wf_id=workflow.getId()
        )
        for workflow in wftool.getWorkflowsFor(obj) or []
    }


def transition(
    obj: DexterityContent,
    transition: str | None = None,
    to_state: str | None = None,
    workflow_id: str | None = None,
    **kwargs: Any,
) -> None:
    """Perform a workflow transition, optionally on a specific workflow.

    With no ``workflow_id`` the transition is routed exactly as
    ``plone.api.content.transition`` routes it — the first workflow in the
    chain that supports the id wins. Pass ``workflow_id`` to address a workflow
    whose transition id is shadowed by an earlier one in the chain.

    :param obj: object to transition.
    :param transition: id of the transition to perform.
    :param to_state: target state, as an alternative to ``transition``. Only
        meaningful for the publication workflow, so it may not be combined with
        ``workflow_id``.
    :param workflow_id: id of the workflow owning the transition.
    :param kwargs: passed through to the workflow, e.g. ``comment``.
    :raises InvalidParameterError: if the transition or workflow is invalid, or
        if ``to_state`` and ``workflow_id`` are combined.
    """
    if workflow_id is None:
        plone_api.content.transition(
            obj=obj, transition=transition, to_state=to_state, **kwargs
        )
        return

    if to_state is not None:
        raise InvalidParameterError(
            "'to_state' cannot be combined with 'workflow_id'; name the "
            "transition explicitly instead."
        )

    wftool = _tool(obj)
    workflow = _workflow(wftool, workflow_id)

    # Mirror what the tool does for the un-targeted path: it selects a workflow
    # with ``isActionSupported`` and raises WorkflowException — which
    # ``plone.api`` turns into InvalidParameterError — when none matches.
    # Calling ``doActionFor`` on a workflow that does not support the action
    # would instead raise Unauthorized, which is not the upstream contract.
    if not workflow.isActionSupported(obj, transition, **kwargs):
        available = sorted(transitions(obj).get(workflow_id, []))
        raise InvalidParameterError(
            "Invalid transition '{}' for workflow '{}'.\n"
            "Valid transitions are:\n{}".format(
                transition, workflow_id, "\n".join(available)
            )
        )

    wftool.doActionFor(obj, transition, wf_id=workflow_id, **kwargs)


def transitions(obj: DexterityContent) -> dict[str, list[str]]:
    """Get the transitions available to the current user, by workflow.

    :param obj: object to inspect.
    :returns: mapping of workflow id to the ids of its available transitions.
        Workflows with nothing available are omitted.
    """
    wftool = _tool(obj)
    owners = owning_workflow(obj)

    available: dict[str, list[str]] = {}
    for action in wftool.listActionInfos(object=obj):
        if action["category"] != "workflow":
            continue
        workflow_id = owners.get(action["id"])
        if workflow_id is None:
            continue
        available.setdefault(workflow_id, []).append(action["id"])
    return available


def conflicting_permissions(obj: DexterityContent) -> dict[str, list[str]]:
    """Find permissions claimed by more than one workflow in the chain.

    Concurrent workflows compose safely as long as the permission sets they
    manage are **disjoint**: ``DCWorkflowDefinition.updateRoleMappingsFor``
    only rewrites the permissions listed in that workflow's own
    ``permissions``, and executing a transition re-applies the mappings of the
    transitioning workflow alone.

    A permission claimed by two workflows is therefore left as whichever of
    them transitioned last wrote it, and stays that way until the other one
    transitions or ``portal_workflow.updateRoleMappings()`` runs. Use this to
    audit a site — from an upgrade step, a test, or a debugging session —
    before trusting a chain's role mappings.

    :param obj: object whose chain is inspected.
    :returns: mapping of permission to the ids of the workflows managing it,
        in chain order. Permissions with a single claimant are omitted, so an
        empty mapping means the chain is conflict-free.
    """
    claimants: dict[str, list[str]] = {}
    for workflow in _tool(obj).getWorkflowsFor(obj) or []:
        # Not every workflow implementation declares managed permissions.
        for permission in getattr(workflow, "permissions", ()) or ():
            claimants.setdefault(permission, []).append(workflow.getId())

    return {
        permission: workflows
        for permission, workflows in claimants.items()
        if len(workflows) > 1
    }


def owning_workflow(obj: DexterityContent) -> dict[str, str]:
    """Map every transition id in the object's chain to its owning workflow.

    A transition id defined by more than one workflow is attributed to the
    first one in chain order, which is exactly how ``doActionFor`` resolves the
    collision.

    :param obj: object whose chain is inspected.
    :returns: mapping of transition id to workflow id.
    """
    owners: dict[str, str] = {}
    for workflow in _tool(obj).getWorkflowsFor(obj) or []:
        definitions = getattr(workflow, "transitions", None)
        if definitions is None:
            # Not every workflow implementation is DCWorkflow-based.
            continue
        for transition_id in definitions.objectIds():
            owners.setdefault(transition_id, workflow.getId())
    return owners
