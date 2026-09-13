"""The checks ``how-to-guides/troubleshoot.md`` gives, one class per symptom.

Each check is run twice where the page says what a failing result means: once
on content where it passes, and once on content set up to fail it the way the
page describes.
"""

from collections.abc import Iterator
from collective.multiworkflow import api as mw_api
from collective.multiworkflow.declaration import collect_contributions
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.demo.behavior import IFoundationMember
from collective.multiworkflow.interfaces import IAdditionalWorkflows
from collective.multiworkflow.testing import add_workflow
from collective.multiworkflow.utils.workflow import format_state
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from plone import api
from plone.dexterity.content import Container
from tests import BASE_CHAIN
from tests import flush_indexing
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
from tests.demo import FOUNDATION_MEMBER_BEHAVIOR
from typing import Any
from zope.interface import alsoProvides

import pytest


pytestmark = pytest.mark.portal(
    content=[MEMBER_PROFILE, PLAIN_DOCUMENT], roles=["Manager"]
)

#: A contributed id no workflow in the site answers to.
MISSING_WORKFLOW = "membership_workflow"

#: A workflow redefining the publication workflow's ``publish``.
COLLIDING_WORKFLOW = "listing_workflow"


class IUndeclared(IAdditionalWorkflows):
    """A participating marker nothing declares a contribution for."""


@pytest.fixture()
def colliding_workflow(wftool: Any, register_contribution: Any) -> Any:
    """Contribute a workflow reusing ``publish`` to the demo profile's chain."""
    workflow = add_workflow(
        wftool,
        COLLIDING_WORKFLOW,
        WORKFLOW_STATES,
        states={"unlisted": ("publish",), "listed": ()},
        initial_state="unlisted",
        transitions=(("publish", "List", "listed"),),
    )
    register_contribution(IFoundationMember, COLLIDING_WORKFLOW)
    return workflow


class TestChainHasOnlyThePublicationWorkflow:
    def test_the_checks_pass_on_participating_content(
        self, wftool: Any, member_profile: Container
    ) -> None:
        obj = member_profile

        assert IAdditionalWorkflows.providedBy(obj)
        assert collect_contributions(obj) == ("foundation_member_workflow",)
        assert wftool.getChainFor(obj) == (
            "simple_publication_workflow",
            "foundation_member_workflow",
        )

    def test_a_type_without_the_behavior_fails_the_first(
        self, wftool: Any, plain_document: Container
    ) -> None:
        assert not IAdditionalWorkflows.providedBy(plain_document)
        assert wftool.getChainFor(plain_document) == BASE_CHAIN

    def test_a_marker_nothing_declares_for_fails_the_second(
        self, wftool: Any, plain_document: Container
    ) -> None:
        alsoProvides(plain_document, IUndeclared)

        assert IAdditionalWorkflows.providedBy(plain_document)
        assert collect_contributions(plain_document) == ()
        assert wftool.getChainFor(plain_document) == BASE_CHAIN

    def test_a_missing_workflow_passes_both_and_is_logged(
        self,
        wftool: Any,
        member_profile: Container,
        register_contribution: Any,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        register_contribution(IFoundationMember, MISSING_WORKFLOW)

        assert MISSING_WORKFLOW in collect_contributions(member_profile)
        assert MISSING_WORKFLOW not in wftool.getChainFor(member_profile)
        assert (
            "Workflow 'membership_workflow' contributed to '/plone/member-profile' "
            "does not exist in portal_workflow; skipping it."
        ) in caplog.messages


class TestTransitionReachesTheWrongWorkflow:
    @pytest.fixture(autouse=True)
    def _setup(
        self, wftool: Any, member_profile: Container, colliding_workflow: Any
    ) -> None:
        self.wftool = wftool
        self.obj = member_profile

    def listing(self) -> str:
        return mw_api.get_state(self.obj, workflow_id=COLLIDING_WORKFLOW)

    def test_the_check_lists_every_claimant(self) -> None:
        wftool = self.wftool
        obj = self.obj
        transition_id = "publish"

        claimants = [
            workflow.getId()
            for workflow in wftool.getWorkflowsFor(obj)
            if transition_id in workflow.transitions.objectIds()
        ]

        assert claimants == [PUBLICATION_WORKFLOW, COLLIDING_WORKFLOW]

    def test_an_unqualified_call_reaches_the_first_workflow(self) -> None:
        mw_api.transition(self.obj, "publish")

        assert api.content.get_state(self.obj) == "published"
        assert self.listing() == "unlisted"

    def test_it_falls_through_when_the_first_cannot_execute_it(self) -> None:
        """From ``published``, the publication workflow has no ``publish``."""
        mw_api.transition(self.obj, "publish")
        mw_api.transition(self.obj, "publish")

        assert self.listing() == "listed"

    def test_naming_the_workflow_reaches_it(self) -> None:
        mw_api.transition(self.obj, "publish", workflow_id=COLLIDING_WORKFLOW)

        assert api.content.get_state(self.obj) == "private"
        assert self.listing() == "listed"


class TestAccessChangesAfterATransition:
    def test_the_check_passes_on_the_demo_chain(
        self, member_profile: Container
    ) -> None:
        obj = member_profile

        assert mw_api.conflicting_permissions(obj) == {}

    def test_an_overlap_fails_it(
        self, member_profile: Container, colliding_workflow: Any
    ) -> None:
        colliding_workflow.permissions = ("View",)

        assert mw_api.conflicting_permissions(member_profile) == {
            "View": [PUBLICATION_WORKFLOW, COLLIDING_WORKFLOW]
        }


class TestSearchFindsNothing:
    @pytest.fixture(autouse=True)
    def _setup(self, catalog: Any, member_profile: Container) -> None:
        flush_indexing()
        self.catalog = catalog

    def test_the_index_checks_pass(self) -> None:
        catalog = self.catalog

        assert "workflow_states" in catalog.indexes()
        assert catalog.Indexes["workflow_states"].numObjects() > 0

    def test_only_a_qualified_value_matches(self) -> None:
        catalog = self.catalog

        assert len(catalog(workflow_states="pending")) == 0

        value = format_state("foundation_member_workflow", "pending")
        assert len(catalog(workflow_states=value)) > 0


class TestExistingContentAfterEnablingTheBehavior:
    @pytest.fixture(autouse=True)
    def _setup(self, catalog: Any, plain_document: Container) -> Iterator[None]:
        flush_indexing()
        fti = api.portal.get_tool("portal_types")[PLAIN_DOCUMENT["type"]]
        fti.manage_changeProperties(
            behaviors=[*fti.behaviors, FOUNDATION_MEMBER_BEHAVIOR]
        )
        self.catalog = catalog
        self.obj = plain_document
        yield

    def found(self) -> int:
        obj = self.obj
        flush_indexing()

        workflow_id = "foundation_member_workflow"
        state = mw_api.get_state(obj, workflow_id=workflow_id)

        catalog = api.portal.get_tool("portal_catalog")
        found = catalog(workflow_states=format_state(workflow_id, state), UID=obj.UID())
        return len(found)

    def test_the_check_fails_before_the_repair(self) -> None:
        assert mw_api.get_state(self.obj, workflow_id=FOUNDATION_MEMBER_WORKFLOW) == (
            "pending"
        )
        assert self.found() == 0

    def test_the_check_passes_after_it(self) -> None:
        self.catalog.reindexIndex("workflow_states", None)

        assert self.found() == 1
