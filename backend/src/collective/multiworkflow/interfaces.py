"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAdditionalWorkflows(Interface):
    """Base marker for content participating in additional workflows.

    A behavior marker interface that contributes extra workflows must extend
    this interface. It is the single registration point for the workflow chain
    adapter: because that adapter is registered for this marker, it is more
    specific than Plone's default :func:`Products.CMFPlone.workflow.
    ToolWorkflowChain` and wins for participating content only — chain lookup
    for every other object is left untouched.

    This interface is never applied directly to content; it is only ever
    extended by a behavior's own marker.
    """


class IAdditionalWorkflowsFor(Interface):
    """The workflow ids one marker contributes to an object's chain.

    Registered as a *subscription* adapter on a behavior's marker interface, so
    that an object providing several participating markers collects the
    contributions of all of them. Declare it with the ZCML directive::

        <plone:additionalworkflows
            marker=".interfaces.IFoundationMember"
            workflows="foundation_member_workflow"
            />

    The factory it registers returns a tuple of workflow ids and declares that
    it provides this interface, mirroring how Plone declares
    ``ToolWorkflowChain`` as providing ``IWorkflowChain``.
    """


class IAdditionalWorkflowLabel(Interface):
    """The label a workflow is shown under, in place of its title.

    Registered as a named utility: the name is the workflow id, and the
    component is the label itself — a message id in the i18n domain of the ZCML
    file declaring it. Declare it with the directive's ``label``::

        <plone:additionalworkflows
            marker=".interfaces.IFoundationMember"
            workflows="foundation_member_workflow"
            label="Foundation membership"
            />

    The label belongs to the workflow rather than to the marker, so it names the
    workflow wherever it appears. Read it with
    :func:`collective.multiworkflow.declaration.workflow_label`, which falls
    back to the workflow's title.
    """
