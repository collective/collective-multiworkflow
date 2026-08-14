"""Spike: how are transitions routed across a composed chain?

Covers per-workflow state reads, routing of a transition to the workflow that
defines it, whether ``review_state`` stays untouched, and what happens when two
workflows in the same chain define the same transition id.
"""

from plone import api
from plone.dexterity.content import Container
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.WorkflowTool import WorkflowTool
from tests import BASE_CHAIN
from tests import PLAIN_DOCUMENT
from tests import SPIKE_COLLIDING_STATE_VAR
from tests import SPIKE_COLLIDING_WORKFLOW
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


class TestTransitionRouting:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        spike_participant: Container,
        spike_workflow: Any,
        spike_chain_adapter: Any,
    ) -> None:
        """A participating Document with the secondary workflow initialized."""
        spike_chain_adapter(SPIKE_WORKFLOW)
        wftool.notifyCreated(spike_participant)
        self.wftool = wftool
        self.doc = spike_participant

    def test_secondary_state_readable(self) -> None:
        """The secondary state variable is readable through the tool."""
        assert self.wftool.getInfoFor(self.doc, SPIKE_STATE_VAR) == "pending"

    def test_review_state_still_readable(self) -> None:
        """Composing the chain leaves ``review_state`` intact."""
        assert self.wftool.getInfoFor(self.doc, "review_state") == "private"

    def test_transition_routes_to_owning_workflow(self) -> None:
        """``doActionFor`` finds the workflow defining the transition."""
        self.wftool.doActionFor(self.doc, "activate")

        assert self.wftool.getInfoFor(self.doc, SPIKE_STATE_VAR) == "active"

    def test_secondary_transition_leaves_review_state_alone(self) -> None:
        """A secondary transition must not move the publication workflow."""
        self.wftool.doActionFor(self.doc, "activate")

        assert self.wftool.getInfoFor(self.doc, "review_state") == "private"

    def test_primary_transition_leaves_secondary_state_alone(self) -> None:
        """Publishing must not move the secondary workflow."""
        with api.env.adopt_roles(["Manager"]):
            self.wftool.doActionFor(self.doc, "publish")

        assert self.wftool.getInfoFor(self.doc, "review_state") == "published"
        assert self.wftool.getInfoFor(self.doc, SPIKE_STATE_VAR) == "pending"

    def test_wf_id_disambiguates_state_read(self) -> None:
        """``getInfoFor`` already accepts an explicit ``wf_id``."""
        state = self.wftool.getInfoFor(self.doc, SPIKE_STATE_VAR, wf_id=SPIKE_WORKFLOW)

        assert state == "pending"

    def test_unknown_transition_raises(self) -> None:
        """An id defined by no workflow in the chain is still an error."""
        with pytest.raises(WorkflowException):
            self.wftool.doActionFor(self.doc, "no_such_transition")


class TestTransitionIdCollision:
    """What happens when two workflows in a chain share a transition id?"""

    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        spike_participant: Container,
        spike_colliding_workflow: Any,
        spike_chain_adapter: Any,
    ) -> None:
        """A participating Document whose extra workflow redefines ``publish``."""
        spike_chain_adapter(SPIKE_COLLIDING_WORKFLOW)
        wftool.notifyCreated(spike_participant)
        self.wftool = wftool
        self.doc = spike_participant

    def test_chain_order_decides_the_winner(self) -> None:
        """The first workflow in chain order supporting the id wins, silently.

        Documents observed behaviour: ``doActionFor`` picks the first workflow
        whose ``isActionSupported`` is true, so the base chain shadows the
        contributed workflow. No error and no warning is raised.
        """
        with api.env.adopt_roles(["Manager"]):
            self.wftool.doActionFor(self.doc, "publish")

        assert self.wftool.getInfoFor(self.doc, "review_state") == "published"
        assert self.wftool.getInfoFor(self.doc, SPIKE_COLLIDING_STATE_VAR) == "unset"

    def test_wf_id_reaches_the_shadowed_workflow(self) -> None:
        """An explicit ``wf_id`` is the escape hatch for a collision."""
        with api.env.adopt_roles(["Manager"]):
            self.wftool.doActionFor(self.doc, "publish", wf_id=SPIKE_COLLIDING_WORKFLOW)

        assert self.wftool.getInfoFor(self.doc, SPIKE_COLLIDING_STATE_VAR) == "flagged"

    def test_base_chain_is_first(self) -> None:
        """The shadowing above follows from the guaranteed chain order."""
        assert self.wftool.getChainFor(self.doc) == (
            *BASE_CHAIN,
            SPIKE_COLLIDING_WORKFLOW,
        )
