"""Registration API for workflow contributions.

A behavior declares the workflows it contributes by registering a subscription
adapter on its own marker interface. This module provides the helper used to
write such a factory, and the lookup that collects every contribution an object
makes.
"""

from .interfaces import IAdditionalWorkflowsFor
from collections.abc import Callable
from typing import Any
from typing import cast
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.interface import Interface


def contributes(
    marker: type[Interface], *workflow_ids: str
) -> Callable[[Any], tuple[str, ...]]:
    """Build a subscription adapter factory contributing ``workflow_ids``.

    Most callers want the ZCML directive instead, which wraps this and
    validates the marker while the configuration is read::

        <plone:additionalworkflows
            marker=".interfaces.IFoundationMember"
            workflows="foundation_member_workflow"
            />

    This function stays public for the cases ZCML cannot express — building a
    contribution from configuration read at start-up, say — where the factory
    is registered by hand and provides
    :class:`~collective.multiworkflow.interfaces.IAdditionalWorkflowsFor`.

    :param marker: the behavior marker interface the factory adapts.
    :param workflow_ids: ids of the workflows this marker contributes.
    :returns: an adapter factory returning ``workflow_ids``.
    """
    ids = tuple(workflow_ids)

    # type-var: zope's stubs type @implementer for classes only, but declaring
    # a *function* factory is the ZCA pattern Plone itself uses for
    # ToolWorkflowChain.
    @adapter(marker)  # type: ignore[type-var]
    @implementer(IAdditionalWorkflowsFor)
    def factory(context: Any) -> tuple[str, ...]:
        return ids

    return factory


def collect_contributions(context: Any) -> tuple[str, ...]:
    """Collect the workflow ids every participating marker contributes.

    Contributions are returned in subscriber registration order, deduplicated,
    keeping the first occurrence of each id.

    :param context: the content object whose contributions are collected.
    :returns: the contributed workflow ids, deduplicated and ordered.
    """
    collected: list[str] = []
    for contribution in subscribers((context,), IAdditionalWorkflowsFor):
        # Subscribers are typed by the interface they provide; the factories
        # built by ``contributes`` actually return the ids as a tuple.
        for workflow_id in cast(tuple[str, ...], contribution):
            if workflow_id not in collected:
                collected.append(workflow_id)
    return tuple(collected)
