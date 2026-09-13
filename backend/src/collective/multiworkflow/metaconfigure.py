"""The ``<plone:additionalworkflows />`` ZCML directive.

Declaring a contribution in Python and wiring it up with a bare
``<subscriber />`` works, but it spreads one decision across two places and
leaves the ``provides=`` interface for the integrator to get right. This
directive is the same registration in one line, and it validates the marker
while the configuration is being read rather than failing silently at runtime.

Modelled on ``plone.behavior``'s ``<plone:behavior />``: a schema describing the
attributes, a handler performing the registration, and a ``meta.zcml`` binding
the two to a namespace.
"""

from .declaration import contributes
from .interfaces import IAdditionalWorkflowLabel
from .interfaces import IAdditionalWorkflows
from .interfaces import IAdditionalWorkflowsFor
from typing import Any
from zope.component.zcml import subscriber
from zope.component.zcml import utility
from zope.configuration.exceptions import ConfigurationError
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import MessageID
from zope.configuration.fields import Tokens
from zope.interface import Interface
from zope.schema import TextLine


class IAdditionalWorkflowsDirective(Interface):
    """Declare the workflows a behavior marker contributes to a chain."""

    marker = GlobalInterface(
        title="Marker interface",
        description=(
            "The behavior's marker interface. It must extend "
            "collective.multiworkflow.interfaces.IAdditionalWorkflows, which "
            "is what makes the chain adapter apply to content providing it."
        ),
        required=True,
    )

    workflows = Tokens(
        title="Workflow ids",
        description=(
            "Ids of the workflows this marker appends to the chain, in order. "
            "Whitespace-separated; they are appended after the workflows the "
            "type is already configured with, never in place of them."
        ),
        value_type=TextLine(),
        required=True,
    )

    label = MessageID(
        title="Label",
        description=(
            "Label the user interface shows for the workflow in place of its "
            "title, translated in the i18n_domain of the ZCML file declaring "
            "it. Only valid when workflows names exactly one workflow."
        ),
        required=False,
    )


def additionalWorkflowsDirective(
    _context: Any,
    marker: type[Interface],
    workflows: list[str],
    label: str | None = None,
) -> None:
    """Register a marker's workflow contribution, and the workflow's label.

    :param _context: the ZCML configuration context.
    :param marker: the behavior marker interface contributing the workflows.
    :param workflows: ids of the contributed workflows, in order.
    :param label: a message id naming the workflow in place of its title, or
        ``None`` to keep the title.
    :raises ConfigurationError: if ``marker`` does not extend
        :class:`~collective.multiworkflow.interfaces.IAdditionalWorkflows`, in
        which case the chain adapter would never apply and the contribution
        would be silently ignored at runtime; or if ``label`` is given while
        ``workflows`` does not name exactly one workflow, which would leave
        unclear which workflow it names.
    """
    if not marker.extends(IAdditionalWorkflows):
        raise ConfigurationError(
            f"{marker.__module__}.{marker.__name__} does not extend "
            "collective.multiworkflow.interfaces.IAdditionalWorkflows, so the "
            "workflow chain adapter would never apply to content providing "
            "it. Make the marker extend IAdditionalWorkflows."
        )

    if label is not None and len(workflows) != 1:
        raise ConfigurationError(
            f"label {label!r} names one workflow, but workflows lists "
            f"{len(workflows)}: {' '.join(workflows)}. Declare each labelled "
            "workflow in a directive of its own."
        )

    subscriber(
        _context,
        for_=(marker,),
        provides=IAdditionalWorkflowsFor,
        factory=contributes(marker, *workflows),
    )

    if label is not None:
        # Keyed by workflow id rather than by marker: the label names the
        # workflow wherever it appears, and two directives labelling the same
        # workflow conflict while the configuration is read.
        utility(
            _context,
            provides=IAdditionalWorkflowLabel,
            component=label,
            name=workflows[0],
        )
