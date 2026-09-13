"""Example behavior: membership tracked alongside publication.

Demonstrates the mechanism end to end. A type with this behavior enabled keeps
its normal publication workflow and gains ``foundation_member_workflow``, which
tracks a membership lifecycle without ever touching ``review_state``.

Its ``state_variable`` is :data:`~collective.multiworkflow.utils.workflow.
WORKFLOW_STATES` rather than a name of its own, which is what makes CMFCore
reindex the catalog on every transition. A real deployment should do the same.

Example material. See :mod:`collective.multiworkflow.demo` for why it lives in
its own subpackage and how to install it; a real deployment declares its own
behavior exactly the same way.
"""

from collective.multiworkflow.interfaces import IAdditionalWorkflows


#: Id of the workflow this behavior contributes, as installed by the demo
#: GenericSetup profile.
FOUNDATION_MEMBER_WORKFLOW = "foundation_member_workflow"

#: The one permission that workflow manages. Deliberately not one of the three
#: the publication workflow manages, so the two chains compose without either
#: overwriting the other's role mappings.
MEMBERSHIP_PERMISSION = "collective.multiworkflow: Manage membership"


class IFoundationMember(IAdditionalWorkflows):
    """Marker for content whose membership status is tracked.

    Extending :class:`~collective.multiworkflow.interfaces.
    IAdditionalWorkflows` is what makes the chain adapter apply: it is
    registered for that base marker, so any behavior extending it participates
    without further wiring.

    The workflows this marker contributes are declared in ``configure.zcml``
    with ``<plone:additionalworkflows />``; nothing else is needed here.
    """
