"""The patterns ``how-to-guides/react-to-another-workflow.md`` shows.

The package couples no workflow to another. Where one has to respond to
another, the how-to shows two ways, both exercised here with the demo
membership workflow and the publication workflow:

- a transition guard that reads the other workflow's state;
- a subscriber to ``IAfterTransitionEvent`` that transitions the other
  workflow.

The guard reads through ``portal_workflow.getInfoFor``, because guard
expressions run as restricted Python, and restricted Python may not import
``collective.multiworkflow.api``. That limit is asserted too.
"""

from collections.abc import Iterator
from collective.multiworkflow import api as mw_api
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.demo.behavior import IFoundationMember
from plone import api
from plone.api.exc import InvalidParameterError
from plone.dexterity.content import Container
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from tests import MEMBER_PROFILE
from typing import Any
from zExceptions import Unauthorized
from zope.component import getGlobalSiteManager

import pytest


pytestmark = pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])

#: The guard expression the how-to shows: activate only published content.
PUBLISHED_ONLY = (
    "python: here.portal_workflow.getInfoFor("
    "here, 'review_state', wf_id='simple_publication_workflow') == 'published'"
)

#: The expression the how-to warns against.
THROUGH_THE_PYTHON_API = (
    "python: modules['collective.multiworkflow.api'].get_state("
    "here, workflow_id='simple_publication_workflow') == 'published'"
)


def set_guard_expression(workflow: Any, transition_id: str, expression: str) -> None:
    """Give a transition a guard expression, keeping its guard permissions.

    :param workflow: the workflow owning the transition.
    :param transition_id: id of the transition to guard.
    :param expression: the TALES expression to guard it with.
    """
    transition = workflow.transitions[transition_id]
    transition.setProperties(
        title=transition.title,
        new_state_id=transition.new_state_id,
        trigger_type=transition.trigger_type,
        script_name=transition.script_name,
        after_script_name=transition.after_script_name,
        actbox_name=transition.actbox_name,
        actbox_url=transition.actbox_url,
        actbox_category=transition.actbox_category,
        actbox_icon=transition.actbox_icon,
        props={
            "guard_permissions": ";".join(transition.getGuard().permissions),
            "guard_expr": expression,
        },
        description=transition.description,
    )


def activate_membership_on_publish(obj: Any, event: Any) -> None:
    """Activate the membership of content as soon as it is published.

    The subscriber the how-to shows, verbatim.
    """
    if event.workflow.getId() != "simple_publication_workflow":
        return
    if event.new_state.getId() != "published":
        return
    if mw_api.get_state(obj, workflow_id="foundation_member_workflow") != "pending":
        return
    mw_api.transition(obj, "activate", workflow_id="foundation_member_workflow")


class TestGuardReadingAnotherWorkflow:
    @pytest.fixture(autouse=True)
    def _setup(self, wftool: Any, member_profile: Container) -> None:
        self.workflow = wftool[FOUNDATION_MEMBER_WORKFLOW]
        self.profile = member_profile

    def membership(self) -> str:
        return mw_api.get_state(self.profile, workflow_id=FOUNDATION_MEMBER_WORKFLOW)

    def test_guard_blocks_while_unpublished(self) -> None:
        """The transition is unavailable while the other workflow disagrees."""
        set_guard_expression(self.workflow, "activate", PUBLISHED_ONLY)

        with pytest.raises(InvalidParameterError):
            mw_api.transition(
                self.profile, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW
            )
        assert self.membership() == "pending"

    def test_guard_allows_once_published(self) -> None:
        """And available as soon as the other workflow reaches the state."""
        set_guard_expression(self.workflow, "activate", PUBLISHED_ONLY)
        api.content.transition(obj=self.profile, transition="publish")

        mw_api.transition(
            self.profile, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW
        )

        assert self.membership() == "active"

    def test_python_api_is_not_importable_in_a_guard(self) -> None:
        """Restricted Python refuses the import, whatever the state."""
        set_guard_expression(self.workflow, "activate", THROUGH_THE_PYTHON_API)
        api.content.transition(obj=self.profile, transition="publish")

        with pytest.raises(Unauthorized):
            self.workflow.isActionSupported(self.profile, "activate")


class TestSubscriberTransitioningAnotherWorkflow:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> Iterator[None]:
        # The global registry is typed as the lookup interface, which does not
        # declare the registration methods it implements.
        gsm: Any = getGlobalSiteManager()
        required = (IFoundationMember, IAfterTransitionEvent)
        gsm.registerHandler(activate_membership_on_publish, required)
        self.profile = member_profile
        yield
        gsm.unregisterHandler(activate_membership_on_publish, required)

    def membership(self) -> str:
        return mw_api.get_state(self.profile, workflow_id=FOUNDATION_MEMBER_WORKFLOW)

    def test_publishing_activates_the_membership(self) -> None:
        """One transition in one workflow drives the other."""
        api.content.transition(obj=self.profile, transition="publish")

        assert api.content.get_state(self.profile) == "published"
        assert self.membership() == "active"

    def test_other_transitions_are_ignored(self) -> None:
        """The subscriber acts on the one transition it names, and no other."""
        api.content.transition(obj=self.profile, transition="submit")

        assert api.content.get_state(self.profile) == "pending"
        assert self.membership() == "pending"

    def test_a_membership_already_moved_is_left_alone(self) -> None:
        """Publishing content whose membership lapsed does not reactivate it."""
        mw_api.transition(
            self.profile, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW
        )
        mw_api.transition(self.profile, "lapse", workflow_id=FOUNDATION_MEMBER_WORKFLOW)
        api.content.transition(obj=self.profile, transition="publish")

        assert self.membership() == "lapsed"
