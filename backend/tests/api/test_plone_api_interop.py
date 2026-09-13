"""How ``plone.api.content`` itself behaves on content with an additional workflow.

These assert ``plone.api``'s behavior, not this package's, so the documentation
can say exactly what a caller who keeps using ``plone.api`` gets. A transition
id defined by two workflows of one chain is covered by
``tests/chain/test_spike_transition_routing.py``.
"""

from collective.multiworkflow import api as mw_api
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from plone import api
from plone.api.exc import InvalidParameterError
from plone.dexterity.content import Container
from tests import MEMBER_PROFILE

import pytest


pytestmark = pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])


class TestPloneApiOnAnAdditionalWorkflow:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> None:
        self.profile = member_profile

    def membership(self) -> str:
        return mw_api.get_state(self.profile, workflow_id=FOUNDATION_MEMBER_WORKFLOW)

    def test_get_state_reads_review_state(self) -> None:
        """``get_state`` answers for the publication workflow only."""
        assert api.content.get_state(self.profile) == "private"

    def test_get_state_takes_no_workflow_id(self) -> None:
        """There is no way to name another workflow through ``plone.api``."""
        with pytest.raises(TypeError):
            api.content.get_state(  # type: ignore[call-arg]
                self.profile, workflow_id=FOUNDATION_MEMBER_WORKFLOW
            )

    def test_transition_reaches_a_unique_id(self) -> None:
        """A transition id no earlier workflow defines is executed."""
        api.content.transition(obj=self.profile, transition="activate")

        assert self.membership() == "active"
        assert api.content.get_state(self.profile) == "private"

    def test_to_state_cannot_reach_an_additional_state(self) -> None:
        """``to_state`` only follows workflows whose status holds ``review_state``."""
        with pytest.raises(InvalidParameterError):
            api.content.transition(obj=self.profile, to_state="active")

        assert self.membership() == "pending"

    def test_to_state_still_drives_publication(self) -> None:
        """And leaves the additional workflow where it was."""
        api.content.transition(obj=self.profile, to_state="published")

        assert api.content.get_state(self.profile) == "published"
        assert self.membership() == "pending"
