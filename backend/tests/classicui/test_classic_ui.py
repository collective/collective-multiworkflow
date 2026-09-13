"""Classic UI's State menu and history viewlet, on a chain of two workflows."""

from plone import api
from plone.app.layout.viewlets.content import WorkflowHistoryViewlet
from plone.dexterity.content import Container
from tests import MEMBER_PROFILE
from zope.browsermenu.interfaces import IBrowserMenu
from zope.component import getUtility

import pytest


pytestmark = pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])


class TestStateMenu:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> None:
        self.profile = member_profile

    def menu_ids(self) -> list[str]:
        menu = getUtility(IBrowserMenu, name="plone_contentmenu_workflow")
        items = menu.getMenuItems(self.profile, self.profile.REQUEST)
        return [item["extra"]["id"] for item in items]

    def test_menu_mixes_every_workflows_transitions(self) -> None:
        """The State menu lists the chain's transitions in one flat list."""
        ids = self.menu_ids()

        assert "workflow-transition-publish" in ids
        assert "workflow-transition-activate" in ids


class TestHistoryViewlet:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> None:
        self.profile = member_profile
        api.content.transition(obj=member_profile, transition="publish")
        api.content.transition(obj=member_profile, transition="activate")

    def actions(self) -> list[str | None]:
        viewlet = WorkflowHistoryViewlet(self.profile, self.profile.REQUEST, None, None)
        viewlet.update()
        return [entry.get("action") for entry in viewlet.workflowHistory()]

    def test_viewlet_shows_the_primary_workflow_only(self) -> None:
        """The viewlet reads ``review_history`` without naming a workflow."""
        actions = self.actions()

        assert "publish" in actions
        assert "activate" not in actions
