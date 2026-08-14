"""Spike: what happens to content that predates the additional workflow?

An object created before its type started participating has no workflow history
for the contributed workflow. This asks whether reads fall back gracefully,
whether transitions work from that fallback, and whether the catalog can index
the secondary state without an explicit migration.
"""

from plone import api
from plone.dexterity.content import Container
from Products.CMFPlone.WorkflowTool import WorkflowTool
from tests import PLAIN_DOCUMENT
from tests import SPIKE_STATE_VAR
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


class TestPreexistingContent:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        spike_participant: Container,
        spike_workflow: Any,
        spike_chain_adapter: Any,
    ) -> None:
        """A Document created *before* the marker and the extra workflow existed.

        ``notifyCreated`` is deliberately not called after marking, so the object
        carries no workflow history for the contributed workflow.
        """
        spike_chain_adapter(SPIKE_WORKFLOW)
        self.wftool = wftool
        self.doc = spike_participant

    def test_no_history_for_contributed_workflow(self) -> None:
        """Precondition: the object genuinely has no status for the workflow."""
        assert self.wftool.getStatusOf(SPIKE_WORKFLOW, self.doc) is None

    def test_read_falls_back_to_initial_state(self) -> None:
        """Reading the secondary state yields the workflow's initial state."""
        assert self.wftool.getInfoFor(self.doc, SPIKE_STATE_VAR) == "pending"

    def test_transitions_available_from_fallback_state(self) -> None:
        """The transitions leaving the initial state are offered."""
        actions = [
            action["id"]
            for action in self.wftool.listActionInfos(object=self.doc)
            if action["category"] == "workflow"
        ]

        assert "activate" in actions

    def test_transition_works_without_migration(self) -> None:
        """Transitioning from the fallback state records real history."""
        self.wftool.doActionFor(self.doc, "activate")

        assert self.wftool.getInfoFor(self.doc, SPIKE_STATE_VAR) == "active"
        assert self.wftool.getStatusOf(SPIKE_WORKFLOW, self.doc) is not None


class TestCatalogIndexing:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        spike_participant: Container,
        spike_workflow: Any,
        spike_chain_adapter: Any,
    ) -> None:
        """As above, plus a FieldIndex for the secondary state variable."""
        spike_chain_adapter(SPIKE_WORKFLOW)
        catalog = api.portal.get_tool("portal_catalog")
        if SPIKE_STATE_VAR not in catalog.indexes():
            catalog.addIndex(SPIKE_STATE_VAR, "FieldIndex")

        self.wftool = wftool
        self.catalog = catalog
        self.doc = spike_participant
        self.doc.reindexObject()

    def test_fallback_state_is_indexed(self) -> None:
        """The secondary state reaches the catalog even with no history."""
        results = self.catalog(**{SPIKE_STATE_VAR: "pending"})

        assert [brain.getPath() for brain in results] == [
            "/".join(self.doc.getPhysicalPath())
        ]

    def test_index_updates_after_transition(self) -> None:
        """A secondary transition reindexes the secondary state."""
        self.wftool.doActionFor(self.doc, "activate")

        assert len(self.catalog(**{SPIKE_STATE_VAR: "active"})) == 1
        assert len(self.catalog(**{SPIKE_STATE_VAR: "pending"})) == 0

    def test_review_state_index_unaffected(self) -> None:
        """The stock ``review_state`` index keeps its usual value."""
        results = self.catalog(review_state="private")

        assert "/".join(self.doc.getPhysicalPath()) in [
            brain.getPath() for brain in results
        ]
