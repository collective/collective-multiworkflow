"""The ``@workflow`` GET service for content with additional workflows.

`plone.restapi`'s own service instantiates ``WorkflowInfo`` directly instead of
looking the adapter up, so overriding the expandable adapter alone changes
``?expand=workflow`` but not the endpoint. This service, registered for the
participation marker, resolves the adapter properly.
"""

from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from typing import cast
from zope.component import getMultiAdapter


class WorkflowChainInfoService(Service):
    """Get workflow information, including every workflow in the chain."""

    def reply(self) -> dict:
        """Return the ``@workflow`` payload.

        :returns: the serialized workflow information for the context.
        """
        info = getMultiAdapter(
            (self.context, self.request), IExpandableElement, name="workflow"
        )
        # IExpandableElement declares no __call__ signature, so its return type
        # is unknown to mypy; every implementation returns the payload mapping.
        payload = cast(dict, info(expand=True))
        return payload["workflow"]
