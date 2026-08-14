"""Spike: does a marker-specific adapter compose the workflow chain?

Validates that ``WorkflowTool.getChainFor`` honours adapter specificity, that
calling the default adapter for the base chain does not recurse, and that
content without the marker is completely unaffected.
"""

from plone.dexterity.content import Container
from Products.CMFPlone.WorkflowTool import WorkflowTool
from tests import BASE_CHAIN
from tests import PLAIN_DOCUMENT
from tests import SPIKE_WORKFLOW
from typing import Any

import pytest


#: Spikes assert Plone's own behaviour, so they carry the ``spike`` marker and
#: can be deselected with ``-m "not spike"``. Content comes from the shared
#: marker rather than being created inline, like every other module here.
pytestmark = [
    pytest.mark.spike,
    pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"]),
]


class TestChainComposition:
    """``spike_participant`` stays a parameter: it marks ``plain_document`` in
    place, so binding both would leave nothing unmarked to compare against.
    """

    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        plain_document: Container,
        spike_workflow: Any,
        spike_chain_adapter: Any,
    ) -> None:
        self.wftool = wftool
        self.plain_document = plain_document
        self.contribute = spike_chain_adapter

    def test_default_chain_unchanged_without_marker(self) -> None:
        """A plain Document keeps the chain configured for its type."""
        assert self.wftool.getChainFor(self.plain_document) == BASE_CHAIN

    def test_marker_appends_workflow(self, spike_participant: Container) -> None:
        """The marked object gets the extra workflow appended, not substituted."""
        self.contribute(SPIKE_WORKFLOW)

        chain = self.wftool.getChainFor(spike_participant)

        assert chain == (*BASE_CHAIN, SPIKE_WORKFLOW)

    def test_lookup_does_not_recurse(self, spike_participant: Container) -> None:
        """Reading the base chain from inside the adapter is recursion-free."""
        self.contribute(SPIKE_WORKFLOW)

        try:
            chain = self.wftool.getChainFor(spike_participant)
        except RecursionError:  # pragma: no cover - the failure being probed
            pytest.fail("Reading the base chain re-entered the chain adapter")

        assert SPIKE_WORKFLOW in chain

    def test_unmarked_content_unaffected_while_adapter_registered(self) -> None:
        """Registering the adapter must not leak into non-participating content."""
        self.contribute(SPIKE_WORKFLOW)

        assert self.wftool.getChainFor(self.plain_document) == BASE_CHAIN

    def test_missing_workflow_is_skipped(self, spike_participant: Container) -> None:
        """A contributed id absent from the tool must not break chain lookup."""
        self.contribute("no_such_workflow")

        assert self.wftool.getChainFor(spike_participant) == BASE_CHAIN

    def test_contribution_is_deduplicated(self, spike_participant: Container) -> None:
        """Contributing a workflow already in the base chain adds nothing."""
        self.contribute(*BASE_CHAIN, SPIKE_WORKFLOW)

        assert self.wftool.getChainFor(spike_participant) == (
            *BASE_CHAIN,
            SPIKE_WORKFLOW,
        )

    def test_both_workflows_are_active(self, spike_participant: Container) -> None:
        """``getWorkflowsFor`` resolves every id in the composed chain."""
        self.contribute(SPIKE_WORKFLOW)

        ids = [wf.getId() for wf in self.wftool.getWorkflowsFor(spike_participant)]

        assert ids == [*BASE_CHAIN, SPIKE_WORKFLOW]
