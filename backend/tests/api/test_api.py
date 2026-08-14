"""Tests for the workflow-aware API helpers.

The defining requirement is that these are a *pure superset* of
``plone.api.content``: called without ``workflow_id`` they must behave
identically to their upstream counterparts, on participating and vanilla
content alike.
"""

from collective.multiworkflow import api as mwapi
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from plone import api
from plone.api.exc import InvalidParameterError
from plone.dexterity.content import Container
from Products.CMFPlone.Portal import PloneSite
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW

import pytest


pytestmark = pytest.mark.portal(
    content=[MEMBER_PROFILE, PLAIN_DOCUMENT],
    roles=["Manager"],
)


class TestGetStateMatchesPloneApi:
    """Without ``workflow_id``, behaviour must be indistinguishable."""

    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container, plain_document: Container) -> None:
        self.plain_document = plain_document
        self.profile = member_profile

    def test_participating_content(self) -> None:
        """Same answer as ``plone.api`` on content with extra workflows."""
        assert mwapi.get_state(self.profile) == api.content.get_state(self.profile)

    def test_vanilla_content(self) -> None:
        """Same answer as ``plone.api`` on ordinary content."""
        assert mwapi.get_state(self.plain_document) == api.content.get_state(
            self.plain_document
        )

    def test_returns_review_state(self) -> None:
        """The value really is the publication state."""
        assert mwapi.get_state(self.profile) == "private"

    def test_default_is_positional(self, portal: PloneSite) -> None:
        """``default`` stays the second positional argument, as upstream."""
        assert mwapi.get_state(portal, "fallback") == "fallback"

    def test_follows_a_publication_transition(self) -> None:
        """It tracks ``review_state``, not a snapshot."""
        api.content.transition(obj=self.profile, transition="publish")

        assert mwapi.get_state(self.profile) == "published"


class TestGetStateWithWorkflowId:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container, plain_document: Container) -> None:
        self.plain_document = plain_document
        self.profile = member_profile

    def test_reads_the_secondary_workflow(self) -> None:
        """A workflow id selects that workflow's own state variable."""
        state = mwapi.get_state(self.profile, workflow_id=FOUNDATION_MEMBER_WORKFLOW)

        assert state == "pending"

    def test_reads_the_primary_workflow_explicitly(self) -> None:
        """Naming the publication workflow gives the same as the default."""
        state = mwapi.get_state(self.profile, workflow_id=PUBLICATION_WORKFLOW)

        assert state == mwapi.get_state(self.profile)

    def test_unknown_workflow_is_rejected(self) -> None:
        """A typo fails loudly rather than returning nonsense."""
        with pytest.raises(InvalidParameterError):
            mwapi.get_state(self.profile, workflow_id="no_such_workflow")

    def test_workflow_not_in_this_chain(self) -> None:
        """A registered workflow the object does not use reports its initial state.

        This mirrors DCWorkflow's own read-path fallback rather than raising.
        """
        state = mwapi.get_state(
            self.plain_document, workflow_id=FOUNDATION_MEMBER_WORKFLOW
        )

        assert state == "pending"


class TestGetStates:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container, plain_document: Container) -> None:
        self.plain_document = plain_document
        self.profile = member_profile

    def test_reports_every_workflow(self) -> None:
        """Participating content reports both workflows."""
        assert mwapi.get_states(self.profile) == {
            PUBLICATION_WORKFLOW: "private",
            FOUNDATION_MEMBER_WORKFLOW: "pending",
        }

    def test_vanilla_content_reports_one(self) -> None:
        """Ordinary content reports only its publication workflow."""
        assert mwapi.get_states(self.plain_document) == {
            PUBLICATION_WORKFLOW: "private"
        }

    def test_chain_order_is_preserved(self) -> None:
        """The mapping follows chain order, publication first."""
        assert list(mwapi.get_states(self.profile)) == [
            PUBLICATION_WORKFLOW,
            FOUNDATION_MEMBER_WORKFLOW,
        ]

    def test_follows_transitions(self) -> None:
        """Both entries track their own workflow independently."""
        api.content.transition(obj=self.profile, transition="publish")
        api.content.transition(obj=self.profile, transition="activate")

        assert mwapi.get_states(self.profile) == {
            PUBLICATION_WORKFLOW: "published",
            FOUNDATION_MEMBER_WORKFLOW: "active",
        }


class TestTransitionMatchesPloneApi:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> None:
        self.profile = member_profile

    def test_routes_without_a_workflow_id(self) -> None:
        """A secondary transition is routed by id, as core does."""
        mwapi.transition(self.profile, transition="activate")

        assert (
            mwapi.get_state(self.profile, workflow_id=FOUNDATION_MEMBER_WORKFLOW)
            == "active"
        )

    def test_publication_transition(self) -> None:
        """The publication workflow is driven exactly as before."""
        mwapi.transition(self.profile, transition="publish")

        assert mwapi.get_state(self.profile) == "published"

    def test_to_state_still_works(self) -> None:
        """The upstream ``to_state`` path is preserved."""
        mwapi.transition(self.profile, to_state="published")

        assert mwapi.get_state(self.profile) == "published"

    def test_invalid_transition_raises(self) -> None:
        """Errors match upstream's exception type."""
        with pytest.raises(InvalidParameterError):
            mwapi.transition(self.profile, transition="no_such_transition")


class TestTransitionWithWorkflowId:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> None:
        self.profile = member_profile

    def test_targets_the_named_workflow(self) -> None:
        """An explicit workflow id drives that workflow."""
        mwapi.transition(
            self.profile,
            transition="activate",
            workflow_id=FOUNDATION_MEMBER_WORKFLOW,
        )

        assert (
            mwapi.get_state(self.profile, workflow_id=FOUNDATION_MEMBER_WORKFLOW)
            == "active"
        )

    def test_leaves_the_other_workflow_alone(self) -> None:
        """The publication state is untouched."""
        mwapi.transition(
            self.profile,
            transition="activate",
            workflow_id=FOUNDATION_MEMBER_WORKFLOW,
        )

        assert mwapi.get_state(self.profile) == "private"

    def test_unknown_workflow_is_rejected(self) -> None:
        """A bad workflow id fails before anything is attempted."""
        with pytest.raises(InvalidParameterError):
            mwapi.transition(self.profile, transition="activate", workflow_id="nope")

    def test_transition_not_in_that_workflow(self) -> None:
        """Asking the wrong workflow for a valid transition is an error."""
        with pytest.raises(InvalidParameterError):
            mwapi.transition(
                self.profile,
                transition="publish",
                workflow_id=FOUNDATION_MEMBER_WORKFLOW,
            )

    def test_to_state_is_rejected(self) -> None:
        """``to_state`` and ``workflow_id`` are mutually exclusive."""
        with pytest.raises(InvalidParameterError):
            mwapi.transition(
                self.profile,
                to_state="published",
                workflow_id=FOUNDATION_MEMBER_WORKFLOW,
            )


class TestTransitions:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container, plain_document: Container) -> None:
        self.plain_document = plain_document
        self.profile = member_profile

    def test_groups_by_workflow(self) -> None:
        """Available transitions are reported per workflow."""
        available = mwapi.transitions(self.profile)

        assert available[FOUNDATION_MEMBER_WORKFLOW] == ["activate"]
        assert "publish" in available[PUBLICATION_WORKFLOW]

    def test_vanilla_content_reports_one_workflow(self) -> None:
        """Ordinary content has only publication transitions."""
        assert set(mwapi.transitions(self.plain_document)) == {PUBLICATION_WORKFLOW}

    def test_follows_a_transition(self) -> None:
        """The set narrows as the workflow advances."""
        mwapi.transition(self.profile, transition="activate")

        assert mwapi.transitions(self.profile)[FOUNDATION_MEMBER_WORKFLOW] == ["lapse"]


class TestOwningWorkflow:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> None:
        self.profile = member_profile

    def test_maps_transitions_to_workflows(self) -> None:
        """Every transition in the chain is attributed to a workflow."""
        owners = mwapi.owning_workflow(self.profile)

        assert owners["activate"] == FOUNDATION_MEMBER_WORKFLOW
        assert owners["publish"] == PUBLICATION_WORKFLOW

    def test_first_workflow_in_chain_wins(self) -> None:
        """Ownership mirrors how ``doActionFor`` resolves a collision."""
        owners = mwapi.owning_workflow(self.profile)

        assert owners["publish"] == PUBLICATION_WORKFLOW
