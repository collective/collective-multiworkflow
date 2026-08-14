"""Spike: does a secondary workflow's ``review_history`` shadow publication's?

**Answer: no, and it cannot.** ``getInfoFor`` walks the chain and takes the
first workflow supporting the variable — the same first-match rule validated
for transitions. But the base chain is *always* first (invariant I1: the
adapter only ever appends), so the publication workflow always wins for
``review_history``. A secondary workflow that declares one is reachable only
via an explicit ``wf_id``.

This corrects an inference made from source reading on 2026-08-07, which had it
backwards. Declaring no ``review_history`` on a secondary workflow is therefore
*not* required for the top-level ``history`` key to stay correct.
"""

from collective.multiworkflow.testing import add_workflow
from plone import api
from plone.dexterity.content import Container
from Products.CMFPlone.WorkflowTool import WorkflowTool
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
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


HISTORY_WORKFLOW = "history_workflow"
HISTORY_STATE_VAR = "history_state"


def _add_history_variable(workflow: Any) -> None:
    """Give a workflow its own ``review_history`` variable.

    Mirrors the definition every stock Plone workflow ships.

    :param workflow: the DCWorkflow definition to extend.
    """
    workflow.variables.addVariable("review_history")
    workflow.variables["review_history"].setProperties(
        description="Provides access to workflow history",
        default_expr="state_change/getHistory",
        for_status=0,
        update_always=0,
        props={"guard_permissions": ""},
    )


@pytest.fixture()
def history_workflow(wftool: Any) -> Any:
    """A secondary workflow that also defines ``review_history``."""
    workflow = add_workflow(
        wftool,
        HISTORY_WORKFLOW,
        HISTORY_STATE_VAR,
        states={"start": ("advance",), "done": ()},
        initial_state="start",
        transitions=(("advance", "Advance", "done"),),
    )
    _add_history_variable(workflow)
    return workflow


class TestWellBehavedSecondaryWorkflow:
    """The supported configuration: no ``review_history`` on the secondary."""

    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        spike_participant: Container,
        spike_workflow: Any,
        spike_chain_adapter: Any,
    ) -> None:
        """Content whose secondary workflow defines no ``review_history``."""
        spike_chain_adapter(SPIKE_WORKFLOW)
        wftool.notifyCreated(spike_participant)
        self.wftool = wftool
        self.doc = spike_participant

    def test_history_comes_from_publication(self) -> None:
        """Publication history is reachable and describes ``review_state``."""
        history = self.wftool.getInfoFor(self.doc, "review_history")

        assert [entry["review_state"] for entry in history] == ["private"]

    def test_history_survives_a_secondary_transition(self) -> None:
        """A secondary transition does not pollute the publication history."""
        self.wftool.doActionFor(self.doc, "activate")

        history = self.wftool.getInfoFor(self.doc, "review_history")

        assert [entry["review_state"] for entry in history] == ["private"]
        assert self.wftool.getInfoFor(self.doc, SPIKE_STATE_VAR) == "active"


class TestSecondaryWorkflowDefiningReviewHistory:
    """A secondary ``review_history`` cannot shadow the publication one."""

    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        spike_participant: Container,
        history_workflow: Any,
        spike_chain_adapter: Any,
    ) -> None:
        """Content whose secondary workflow *does* define ``review_history``."""
        spike_chain_adapter(HISTORY_WORKFLOW)
        wftool.notifyCreated(spike_participant)
        self.wftool = wftool
        self.doc = spike_participant

    def test_publication_history_still_wins(self) -> None:
        """First match in chain order wins, and the base chain is always first.

        Because the adapter only ever *appends* (I1), the publication workflow
        precedes every contributed workflow, so it answers ``review_history``
        even when a secondary workflow also defines it.
        """
        history = self.wftool.getInfoFor(self.doc, "review_history")

        states = [entry.get("review_state") for entry in history]
        assert states == ["private"], (
            f"Expected publication history, got entries {history!r}"
        )

    def test_explicit_wf_id_always_reaches_publication(self) -> None:
        """``wf_id`` disambiguates variables exactly as it does transitions."""
        history = self.wftool.getInfoFor(
            self.doc, "review_history", wf_id=PUBLICATION_WORKFLOW
        )

        assert [entry["review_state"] for entry in history] == ["private"]

    def test_secondary_history_is_reachable_by_wf_id(self) -> None:
        """The secondary workflow's own history is separately addressable."""
        with api.env.adopt_roles(["Manager"]):
            self.wftool.doActionFor(self.doc, "advance")

        history = self.wftool.getInfoFor(
            self.doc, "review_history", wf_id=HISTORY_WORKFLOW
        )

        assert [entry.get(HISTORY_STATE_VAR) for entry in history] == ["start", "done"]
