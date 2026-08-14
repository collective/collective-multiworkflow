"""Functional tests for the ``@history`` endpoint.

Core builds its listing from an untargeted ``review_history`` read, which
always resolves to the first workflow in the chain — so an additional
workflow's transitions are simply absent. These tests pin the fix: the same
flat, time-sorted stream, with the missing entries merged in and every entry
attributed to a workflow.
"""

from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
from typing import Any

import pytest


pytestmark = pytest.mark.portal(
    content=[MEMBER_PROFILE, PLAIN_DOCUMENT],
    roles=["Manager"],
)


def workflow_entries(history: list, workflow_id: str) -> list:
    """Return the entries one workflow recorded.

    :param history: an ``@history`` listing.
    :param workflow_id: the workflow to filter on.
    :returns: that workflow's entries, in listing order.
    """
    return [entry for entry in history if entry.get("workflow_id") == workflow_id]


class TestEveryEntryIsAttributed:
    @pytest.fixture(autouse=True)
    def _setup(self, member_history: list) -> None:
        self.history = member_history

    def test_all_entries_carry_the_key(self) -> None:
        """``workflow_id`` is unconditional, so clients can rely on it."""
        assert all("workflow_id" in entry for entry in self.history)

    def test_workflow_entries_name_their_workflow(self) -> None:
        """No workflow entry is left unattributed."""
        for entry in self.history:
            if entry["type"] == "workflow":
                assert entry["workflow_id"] is not None

    def test_versioning_entries_have_no_workflow(self) -> None:
        """A version is not a transition, so it belongs to no workflow."""
        for entry in self.history:
            if entry["type"] == "versioning":
                assert entry["workflow_id"] is None

    def test_publication_entries_are_attributed(self) -> None:
        """The entries core already returned are tagged, not replaced."""
        assert workflow_entries(self.history, PUBLICATION_WORKFLOW)


class TestAdditionalWorkflowAppears:
    """These drive a transition, so they re-fetch rather than use ``history``."""

    @pytest.fixture(autouse=True)
    def _setup(
        self, committed_portal: Any, manager_request: Any, member_history: list
    ) -> None:
        self.request = manager_request
        self.history = member_history

    def activate(self) -> list:
        """Perform the membership transition and return the fresh listing.

        :returns: the ``@history`` payload after the transition.
        """
        self.request.post(f"/{MEMBER_PROFILE['id']}/@workflow/activate")
        return self.request.get(f"/{MEMBER_PROFILE['id']}/@history").json()

    def test_secondary_creation_entry_is_present(self) -> None:
        """The additional workflow's own history reaches the listing."""
        assert workflow_entries(self.history, FOUNDATION_MEMBER_WORKFLOW)

    def test_secondary_transition_is_listed(self) -> None:
        """A membership transition shows up like a publication one."""
        history = self.activate()

        titles = [
            entry["transition_title"]
            for entry in workflow_entries(history, FOUNDATION_MEMBER_WORKFLOW)
        ]
        assert "Activate" in titles

    def test_secondary_state_title_is_resolved(self) -> None:
        """Titles come from the workflow, not from the type's chain."""
        history = self.activate()

        entries = workflow_entries(history, FOUNDATION_MEMBER_WORKFLOW)
        assert entries[0]["state_title"] == "Active"

    def test_secondary_entry_carries_an_actor(self) -> None:
        """Entries are shaped exactly like the ones core emits."""
        history = self.activate()

        actor = workflow_entries(history, FOUNDATION_MEMBER_WORKFLOW)[0]["actor"]
        assert actor["id"] is not None
        assert actor["@id"].endswith(f"/@users/{actor['id']}")

    def test_publication_entries_are_not_lost(self) -> None:
        """Merging must be additive; nothing core reported may disappear."""
        before = len(workflow_entries(self.history, PUBLICATION_WORKFLOW))

        history = self.activate()

        assert len(workflow_entries(history, PUBLICATION_WORKFLOW)) == before


class TestListingIsStillOrdered:
    @pytest.fixture(autouse=True)
    def _setup(self, committed_portal: Any, manager_request: Any) -> None:
        manager_request.post(f"/{MEMBER_PROFILE['id']}/@workflow/activate")
        self.history = manager_request.get(f"/{MEMBER_PROFILE['id']}/@history").json()

    def test_newest_first(self) -> None:
        """The merged stream keeps core's ordering contract."""
        times = [entry["time"] for entry in self.history]

        assert times == sorted(times, reverse=True)

    def test_latest_transition_leads(self) -> None:
        """The most recent transition is the first entry, whichever workflow."""
        assert self.history[0]["workflow_id"] == FOUNDATION_MEMBER_WORKFLOW


class TestNonParticipatingContentIsUntouched:
    @pytest.fixture(autouse=True)
    def _setup(self, plain_history: list) -> None:
        self.history = plain_history

    def test_no_workflow_id_key(self) -> None:
        """Vanilla content is served by core's own service, unchanged."""
        assert all("workflow_id" not in entry for entry in self.history)

    def test_publication_history_is_present(self) -> None:
        """And it still reports what it always did."""
        assert self.history
