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
