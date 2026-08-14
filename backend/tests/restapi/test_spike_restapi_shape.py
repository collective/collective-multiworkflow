"""Spike: can the ``@workflow`` endpoint be extended without forking it?

Two things need proving before the serializer work is designed:

1. Whether overriding the named ``workflow`` expandable adapter is enough to
   change the endpoint's response, or whether the service registration must be
   overridden too.
2. What the *existing* payload looks like once a second workflow is in the
   chain — specifically whether secondary transitions leak into the flat,
   top-level ``transitions`` list that current clients already consume.
"""

from plone.dexterity.content import Container
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services.workflow.info import WorkflowInfo
from plone.restapi.services.workflow.info import WorkflowInfoService
from Products.CMFPlone.WorkflowTool import WorkflowTool
from Products.Five.browser import BrowserView
from tests import IExtraWorkflows
from tests import PLAIN_DOCUMENT
from tests import SPIKE_WORKFLOW
from typing import Any
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import pytest


#: Spikes assert Plone's own behaviour, so they carry the ``spike`` marker and
#: can be deselected with ``-m "not spike"``. Content comes from the shared
#: marker rather than being created inline, like every other module here.
pytestmark = [
    pytest.mark.spike,
    pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"]),
]


def call_service(context: Any, request: Any) -> dict:
    """Invoke the stock ``@workflow`` GET service against an object.

    The ``plone:service`` directive builds its view class as
    ``type(name, (factory, BrowserView), ...)``, so the service class alone has
    no ``__init__``. This mirrors that synthesis to reach ``reply()``.

    :param context: the content object to serialize.
    :param request: the current request.
    :returns: the endpoint's response body as a dict.
    """
    service_class = type(
        "WorkflowInfoServiceView", (WorkflowInfoService, BrowserView), {}
    )
    return service_class(context, request).reply()


@pytest.fixture()
def override_workflow_adapter() -> Any:
    """Register a marker-specific ``workflow`` expandable adapter."""
    gsm = getGlobalSiteManager()

    @implementer(IExpandableElement)
    @adapter(IExtraWorkflows, Interface)
    class ExtendedWorkflowInfo(WorkflowInfo):
        def __call__(self, expand: bool = False) -> dict:
            result = super().__call__(expand=expand)
            if expand:
                result["workflow"]["chain"] = ["sentinel"]
            return result

    gsm.registerAdapter(ExtendedWorkflowInfo, name="workflow")
    yield ExtendedWorkflowInfo
    gsm.unregisterAdapter(ExtendedWorkflowInfo, name="workflow")


class TestExistingPayload:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        spike_participant: Container,
        spike_workflow: Any,
        spike_chain_adapter: Any,
        http_request: Any,
    ) -> None:
        """A participating Document with both workflows active."""
        spike_chain_adapter(SPIKE_WORKFLOW)
        wftool.notifyCreated(spike_participant)
        self.request = http_request
        self.payload = call_service(spike_participant, http_request)

    def test_secondary_transitions_leak_into_flat_list(self) -> None:
        """The stock top-level ``transitions`` list mixes in secondary ones.

        This is the backward-compatibility problem: a client reading
        ``transitions`` cannot tell a publication transition from a secondary
        one, because ``listActionInfos`` walks the whole chain.
        """
        titles = {transition["title"] for transition in self.payload["transitions"]}

        assert "Activate" in titles

    def test_top_level_state_is_review_state(self) -> None:
        """The top-level ``state`` key still reports ``review_state`` only."""
        assert self.payload["state"]["id"] == "private"

    def test_payload_has_no_chain_key_yet(self) -> None:
        """Nothing in core exposes the per-workflow breakdown."""
        assert "chain" not in self.payload


class TestExtensionPoint:
    """``plain_document`` stays a parameter: one test needs it *unmarked*, and
    ``spike_participant`` marks it in place.
    """

    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        spike_workflow: Any,
        spike_chain_adapter: Any,
        http_request: Any,
        override_workflow_adapter: Any,
    ) -> None:
        self.wftool = wftool
        self.request = http_request
        self.contribute = spike_chain_adapter

    def participant(self, spike_participant: Container) -> Container:
        """Finish wiring a marked Document up for the chain.

        :param spike_participant: the marked Document.
        :returns: the same object, with the secondary workflow initialized.
        """
        self.contribute(SPIKE_WORKFLOW)
        self.wftool.notifyCreated(spike_participant)
        return spike_participant

    def test_service_ignores_the_overridden_adapter(
        self, spike_participant: Container
    ) -> None:
        """Overriding the adapter alone does not change the endpoint.

        ``WorkflowInfoService.reply`` instantiates ``WorkflowInfo`` directly
        instead of looking the adapter up, so the service registration has to be
        overridden as well.
        """
        payload = call_service(self.participant(spike_participant), self.request)

        assert "chain" not in payload

    def test_overridden_adapter_does_win_on_expansion(
        self, spike_participant: Container
    ) -> None:
        """Adapter lookup — used by ``?expand=workflow`` — does honour it."""
        info = getMultiAdapter(
            (self.participant(spike_participant), self.request),
            IExpandableElement,
            name="workflow",
        )
        payload = info(expand=True)

        assert payload["workflow"]["chain"] == ["sentinel"]

    def test_unmarked_content_keeps_default_adapter(
        self, plain_document: Container
    ) -> None:
        """Vanilla content is untouched by the marker-specific registration."""
        info = getMultiAdapter(
            (plain_document, self.request), IExpandableElement, name="workflow"
        )
        payload = info(expand=True)

        assert "chain" not in payload["workflow"]
