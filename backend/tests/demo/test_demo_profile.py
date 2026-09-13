"""End-to-end tests for the example behavior and its demo profile.

Exercises the whole mechanism the way a site would: create content of the
participating type, transition the secondary workflow, and search on its state.
The demo profile is applied by the test layer, so no test applies it here.
"""

from . import FOUNDATION_MEMBER_BEHAVIOR
from collective.multiworkflow import api as mwapi
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.demo.behavior import IFoundationMember
from collective.multiworkflow.demo.behavior import MEMBERSHIP_PERMISSION
from collective.multiworkflow.utils.workflow import format_state
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from plone import api
from plone.dexterity.content import Container
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.WorkflowTool import WorkflowTool
from tests import BASE_CHAIN
from tests import flush_indexing
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
from tests import roles_for
from typing import Any

import pytest


class TestDemoProfileInstall:
    @pytest.fixture(autouse=True)
    def _setup(self, wftool: WorkflowTool, catalog: Any, get_behaviors: Any) -> None:
        self.wftool = wftool
        self.catalog = catalog
        self.get_behaviors = get_behaviors

    def test_workflow_is_installed(self) -> None:
        """The demo profile adds the workflow definition to the tool."""
        assert FOUNDATION_MEMBER_WORKFLOW in self.wftool.objectIds()

    def test_workflow_uses_the_shared_state_variable(self) -> None:
        """It never drives ``review_state``, and adopts the indexed name.

        Adopting it is what puts the index into the set CMFCore reindexes on
        every transition, so this assertion guards the freshness contract as
        much as it guards the profile.
        """
        workflow = self.wftool[FOUNDATION_MEMBER_WORKFLOW]

        assert workflow.state_var == WORKFLOW_STATES

    def test_workflow_manages_its_own_permission(self) -> None:
        """An additional workflow may manage permissions of its own."""
        workflow = self.wftool[FOUNDATION_MEMBER_WORKFLOW]

        assert tuple(workflow.permissions) == (MEMBERSHIP_PERMISSION,)

    def test_managed_permissions_are_disjoint_from_publication(self) -> None:
        """The supported configuration: no permission claimed twice."""
        publication = self.wftool[PUBLICATION_WORKFLOW]
        secondary = self.wftool[FOUNDATION_MEMBER_WORKFLOW]

        assert not set(publication.permissions) & set(secondary.permissions)

    def test_workflow_is_not_bound_to_any_type(self) -> None:
        """The workflow reaches content through the adapter, not the tool."""
        for chain in self.wftool._chains_by_type.values():
            assert FOUNDATION_MEMBER_WORKFLOW not in chain

    def test_behavior_is_enabled_on_the_profile_type(self) -> None:
        """The type the profile introduces carries the behavior."""
        assert FOUNDATION_MEMBER_BEHAVIOR in self.get_behaviors(MEMBER_PROFILE["type"])

    def test_stock_types_are_left_alone(self) -> None:
        """And no type Plone already shipped is modified."""
        assert FOUNDATION_MEMBER_BEHAVIOR not in self.get_behaviors(
            PLAIN_DOCUMENT["type"]
        )

    def test_state_index_is_installed(self) -> None:
        """The chain index comes from the add-on, not from this profile.

        A profile contributing a workflow ships no ``catalog.xml`` of its own;
        that is the whole point of one index covering the chain.
        """
        assert WORKFLOW_STATES in self.catalog.indexes()


@pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])
class TestBehaviorDrivesTheChain:
    @pytest.fixture(autouse=True)
    def _setup(self, wftool: WorkflowTool, member_profile: Container) -> None:
        self.wftool = wftool
        self.profile = member_profile

    def test_profile_provides_the_marker(self) -> None:
        """Enabling the behavior marks new content with its interface."""
        assert IFoundationMember.providedBy(self.profile)

    def test_chain_gains_the_workflow(self) -> None:
        """The contributed workflow is appended to the configured chain."""
        assert self.wftool.getChainFor(self.profile) == (
            *BASE_CHAIN,
            FOUNDATION_MEMBER_WORKFLOW,
        )

    def test_initial_state(self) -> None:
        """New content starts in the workflow's initial state."""
        assert self.wftool.getInfoFor(self.profile, WORKFLOW_STATES) == "pending"

    def test_review_state_is_normal(self) -> None:
        """Publication behaves exactly as on any other content."""
        assert self.wftool.getInfoFor(self.profile, "review_state") == "private"

    def test_other_types_are_unaffected(self, portal: PloneSite) -> None:
        """A type without the behavior keeps its plain chain."""
        news = api.content.create(
            container=portal, type="News Item", id="news", title="News"
        )

        assert self.wftool.getChainFor(news) == BASE_CHAIN


@pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])
class TestMembershipLifecycle:
    @pytest.fixture(autouse=True)
    def _setup(self, wftool: WorkflowTool, member_profile: Container) -> None:
        self.wftool = wftool
        self.profile = member_profile

    def test_activate(self) -> None:
        """The membership transition moves only the membership state."""
        api.content.transition(obj=self.profile, transition="activate")

        assert self.wftool.getInfoFor(self.profile, WORKFLOW_STATES) == "active"
        assert self.wftool.getInfoFor(self.profile, "review_state") == "private"

    def test_lapse_then_reactivate(self) -> None:
        """The lifecycle round-trips through its states."""
        api.content.transition(obj=self.profile, transition="activate")
        api.content.transition(obj=self.profile, transition="lapse")
        api.content.transition(obj=self.profile, transition="activate")

        assert self.wftool.getInfoFor(self.profile, WORKFLOW_STATES) == "active"

    def test_publishing_leaves_membership_alone(self) -> None:
        """The two workflows are genuinely independent."""
        api.content.transition(obj=self.profile, transition="publish")

        assert self.wftool.getInfoFor(self.profile, "review_state") == "published"
        assert self.wftool.getInfoFor(self.profile, WORKFLOW_STATES) == "pending"

    def test_both_workflows_transition_independently(self) -> None:
        """Driving both leaves each in its own expected state."""
        api.content.transition(obj=self.profile, transition="publish")
        api.content.transition(obj=self.profile, transition="activate")

        assert self.wftool.getInfoFor(self.profile, "review_state") == "published"
        assert self.wftool.getInfoFor(self.profile, WORKFLOW_STATES) == "active"


@pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])
class TestPermissionsCompose:
    """The two workflows manage disjoint permission sets, so neither loses."""

    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> None:
        self.profile = member_profile

    def test_initial_state_applies_its_mapping(self) -> None:
        """The secondary workflow's map is written when content is created."""
        assert roles_for(self.profile, MEMBERSHIP_PERMISSION) == (
            "Manager",
            "Reviewer",
            "Site Administrator",
        )

    def test_secondary_transition_rewrites_it(self) -> None:
        """Each state maps the permission differently."""
        api.content.transition(obj=self.profile, transition="activate")

        assert roles_for(self.profile, MEMBERSHIP_PERMISSION) == (
            "Manager",
            "Owner",
            "Site Administrator",
        )

    def test_publication_leaves_the_secondary_mapping_alone(self) -> None:
        """The disjoint-sets guarantee, stated as the behaviour it produces."""
        api.content.transition(obj=self.profile, transition="activate")
        before = roles_for(self.profile, MEMBERSHIP_PERMISSION)

        api.content.transition(obj=self.profile, transition="publish")

        assert roles_for(self.profile, MEMBERSHIP_PERMISSION) == before

    def test_membership_leaves_the_publication_mapping_alone(self) -> None:
        """And symmetrically, in the direction that would break a live site."""
        api.content.transition(obj=self.profile, transition="publish")
        before = roles_for(self.profile, "Modify portal content")

        api.content.transition(obj=self.profile, transition="activate")

        assert roles_for(self.profile, "Modify portal content") == before

    def test_chain_reports_no_conflict(self) -> None:
        """The audit helper agrees the demo chain is safe."""
        assert mwapi.conflicting_permissions(self.profile) == {}


@pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])
class TestMembershipIsSearchable:
    @pytest.fixture(autouse=True)
    def _setup(self, catalog: Any, member_profile: Container) -> None:
        self.catalog = catalog
        self.profile = member_profile

    def _search(self, state: str) -> list:
        """Find content by its membership state.

        ``flush_indexing`` first: an index assertion made against an unflushed
        catalog measures the indexing queue, not the code under test.

        :param state: id of the membership state to search for.
        :returns: the brains the index answers with.
        """
        flush_indexing()
        return list(
            self.catalog(**{
                WORKFLOW_STATES: format_state(FOUNDATION_MEMBER_WORKFLOW, state)
            })
        )

    def test_new_content_is_indexed(self) -> None:
        """The initial membership state reaches the catalog."""
        assert [brain.getPath() for brain in self._search("pending")] == [
            "/".join(self.profile.getPhysicalPath())
        ]

    def test_index_follows_transitions(self) -> None:
        """Transitioning reindexes the secondary state."""
        api.content.transition(obj=self.profile, transition="activate")

        assert len(self._search("active")) == 1
        assert len(self._search("pending")) == 0

    def test_the_query_is_qualified_by_workflow(self) -> None:
        """A bare state id matches nothing: values carry their workflow."""
        flush_indexing()

        assert len(self.catalog(**{WORKFLOW_STATES: "pending"})) == 0

    def test_metadata_column_is_available(self) -> None:
        """The whole chain is usable as brain metadata, for listings."""
        brain = self._search("pending")[0]

        assert getattr(brain, WORKFLOW_STATES) == (
            format_state(PUBLICATION_WORKFLOW, "private"),
            format_state(FOUNDATION_MEMBER_WORKFLOW, "pending"),
        )
