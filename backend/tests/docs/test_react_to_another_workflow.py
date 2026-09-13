"""The patterns ``how-to-guides/react-to-another-workflow.md`` shows.

The package couples no workflow to another. Where one has to respond to
another, the how-to shows two ways, both exercised here with the demo
membership workflow and the publication workflow:

- a transition guard that reads the other workflow's state, declared in the
  workflow's ``definition.xml``;
- a subscriber to ``IAfterTransitionEvent`` that transitions the other
  workflow, registered in ZCML.

The guard reads through ``portal_workflow.getInfoFor``, because guard
expressions run as restricted Python, and restricted Python may not import
``collective.multiworkflow.api``. That limit is asserted too.

The XML and the ZCML below are the snippets the how-to shows, and they reach the
site the way they would in a real package: the XML through DCWorkflow's own
definition parser, the ZCML through ``xmlconfig``.
"""

from . import subscribers
from collections.abc import Iterator
from collective.multiworkflow import api as mw_api
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.demo.behavior import IFoundationMember
from importlib.resources import files
from plone import api
from plone.api.exc import InvalidParameterError
from plone.dexterity.content import Container
from Products.DCWorkflow import exportimport as dcworkflow_import
from Products.DCWorkflow.exportimport import WorkflowDefinitionConfigurator
from Products.DCWorkflow.interfaces import IAfterTransitionEvent
from tests import MEMBER_PROFILE
from tests import PUBLICATION_WORKFLOW
from typing import Any
from zExceptions import Unauthorized
from zope.component import getGlobalSiteManager
from zope.component.hooks import getSite
from zope.component.hooks import setSite
from zope.configuration import xmlconfig

import pytest
import re
import tests.docs
import zope.component


pytestmark = pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])

#: The guard expression the how-to shows: activate only published content.
PUBLISHED_ONLY = (
    "python: here.portal_workflow.getInfoFor("
    "here, 'review_state', wf_id='simple_publication_workflow') == 'published'"
)

#: The same guard in the other direction: publish only active members.
ACTIVE_MEMBERS_ONLY = (
    "python: here.portal_workflow.getInfoFor("
    "here, 'workflow_states', wf_id='foundation_member_workflow') == 'active'"
)

#: The expression the how-to warns against.
THROUGH_THE_PYTHON_API = (
    "python: modules['collective.multiworkflow.api'].get_state("
    "here, workflow_id='simple_publication_workflow') == 'published'"
)

#: The demo's ``activate`` transition with the guard added, as the how-to shows.
GUARDED_TRANSITION = """\
<transition after_script=""
            before_script=""
            new_state="active"
            title="Activate membership"
            transition_id="activate"
            trigger="USER"
>
  <description>Approve or renew the membership.</description>
  <action category="workflow"
          icon=""
          url="%(content_url)s/content_status_modify?workflow_action=activate"
  >Activate</action>
  <guard>
    <guard-permission>Modify portal content</guard-permission>
    <guard-expression>python: here.portal_workflow.getInfoFor(here, 'review_state', wf_id='simple_publication_workflow') == 'published'</guard-expression>
  </guard>
</transition>
"""

#: The registration the how-to shows, relative to the package holding it.
SUBSCRIBER_ZCML = """\
<configure xmlns="http://namespaces.zope.org/zope">

  <subscriber
      for="collective.multiworkflow.demo.behavior.IFoundationMember
           Products.DCWorkflow.interfaces.IAfterTransitionEvent"
      handler=".subscribers.activate_membership_on_publish"
      />

</configure>
"""

#: What the ZCML above registers, to unregister it afterwards.
REQUIRED = (IFoundationMember, IAfterTransitionEvent)

#: The demo workflow definition the guarded transition is spliced into.
DEFINITION = (
    files("collective.multiworkflow.demo")
    / "profiles"
    / "demo"
    / "workflows"
    / FOUNDATION_MEMBER_WORKFLOW
    / "definition.xml"
)


def import_definition(workflow: Any, transition_xml: str) -> None:
    """Import the demo definition into a workflow, with one transition replaced.

    Parses and applies the definition exactly as the GenericSetup import step
    does, so a guard that works here works from a profile.

    :param workflow: the workflow to import the definition into.
    :param transition_xml: the ``<transition>`` element replacing the one with
        the same ``transition_id``.
    """
    transition_id = re.search(r'transition_id="([^"]+)"', transition_xml)
    assert transition_id is not None
    xml = DEFINITION.read_text(encoding="utf-8")
    existing = re.search(
        rf'<transition [^>]*transition_id="{transition_id.group(1)}"[^>]*>'
        r".*?</transition>\n",
        xml,
        re.DOTALL,
    )
    assert existing is not None
    xml = xml[: existing.start()] + transition_xml + xml[existing.end() :]

    (
        _workflow_id,
        title,
        state_variable,
        initial_state,
        states,
        transitions,
        variables,
        worklists,
        permissions,
        groups,
        scripts,
        description,
        manager_bypass,
        creation_guard,
    ) = WorkflowDefinitionConfigurator(workflow).parseWorkflowXML(xml.encode("utf-8"))
    # attr-defined: plone-stubs declares the module's public names only, and
    # this private helper is the one the GenericSetup import step calls.
    dcworkflow_import._initDCWorkflow(  # type: ignore[attr-defined]
        workflow,
        title,
        description,
        manager_bypass,
        creation_guard,
        state_variable,
        initial_state,
        states,
        transitions,
        variables,
        worklists,
        permissions,
        groups,
        scripts,
        None,
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


def activate_without_checking(obj: Any, event: Any) -> None:
    """The subscriber above without its check on the membership state."""
    if event.workflow.getId() != PUBLICATION_WORKFLOW:
        return
    if event.new_state.getId() != "published":
        return
    mw_api.transition(obj, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW)


class TestGuardInTheDefinition:
    @pytest.fixture(autouse=True)
    def _setup(self, wftool: Any, member_profile: Container) -> None:
        self.workflow = wftool[FOUNDATION_MEMBER_WORKFLOW]
        import_definition(self.workflow, GUARDED_TRANSITION)
        self.profile = member_profile

    def membership(self) -> str:
        return mw_api.get_state(self.profile, workflow_id=FOUNDATION_MEMBER_WORKFLOW)

    def test_the_guard_is_imported(self) -> None:
        """The expression is added, and the guard permission kept."""
        guard = self.workflow.transitions["activate"].getGuard()

        assert guard.getExprText() == PUBLISHED_ONLY
        assert tuple(guard.permissions) == ("Modify portal content",)

    def test_guard_blocks_while_unpublished(self) -> None:
        """The transition is unavailable while the other workflow disagrees."""
        with pytest.raises(InvalidParameterError):
            mw_api.transition(
                self.profile, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW
            )
        assert self.membership() == "pending"

    def test_guard_allows_once_published(self) -> None:
        """And available as soon as the other workflow reaches the state."""
        api.content.transition(obj=self.profile, transition="publish")

        mw_api.transition(
            self.profile, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW
        )

        assert self.membership() == "active"

    def test_guard_is_not_checked_again_later(self) -> None:
        """Retracting afterwards leaves the membership where it is."""
        api.content.transition(obj=self.profile, transition="publish")
        mw_api.transition(
            self.profile, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW
        )

        api.content.transition(obj=self.profile, transition="retract")

        assert api.content.get_state(self.profile) == "private"
        assert self.membership() == "active"


class TestGuardInTheOtherDirection:
    @pytest.fixture(autouse=True)
    def _setup(self, wftool: Any, member_profile: Container) -> None:
        set_guard_expression(
            wftool[PUBLICATION_WORKFLOW], "publish", ACTIVE_MEMBERS_ONLY
        )
        self.profile = member_profile

    def test_publishing_is_blocked_while_pending(self) -> None:
        """The publication workflow can wait on an additional workflow too."""
        with pytest.raises(InvalidParameterError):
            api.content.transition(obj=self.profile, transition="publish")
        assert api.content.get_state(self.profile) == "private"

    def test_publishing_is_allowed_once_active(self) -> None:
        mw_api.transition(
            self.profile, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW
        )

        api.content.transition(obj=self.profile, transition="publish")

        assert api.content.get_state(self.profile) == "published"


class TestPythonApiInAGuard:
    def test_python_api_is_not_importable_in_a_guard(
        self, wftool: Any, member_profile: Container
    ) -> None:
        """Restricted Python refuses the import, whatever the state."""
        workflow = wftool[FOUNDATION_MEMBER_WORKFLOW]
        set_guard_expression(workflow, "activate", THROUGH_THE_PYTHON_API)
        api.content.transition(obj=member_profile, transition="publish")

        with pytest.raises(Unauthorized):
            workflow.isActionSupported(member_profile, "activate")


class TestSubscriberTransitioningAnotherWorkflow:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> Iterator[None]:
        context = xmlconfig.file("meta.zcml", zope.component)
        context.package = tests.docs
        # The subscriber directive registers into whatever getSiteManager()
        # returns. With the portal as the active site that is the portal's
        # persistent registry, so step out of it while the ZCML is read.
        site = getSite()
        # arg-type: the stubs demand a site, but None is how zope.component
        # clears the active one.
        setSite(None)  # type: ignore[arg-type]
        try:
            xmlconfig.string(SUBSCRIBER_ZCML, context=context)
        finally:
            setSite(site)
        self.profile = member_profile
        yield
        # The global registry is typed as the lookup interface, which does not
        # declare the registration methods it implements.
        gsm: Any = getGlobalSiteManager()
        # False would mean the ZCML registered somewhere else, and every test
        # above passed against a registration this teardown cannot see.
        assert gsm.unregisterHandler(
            subscribers.activate_membership_on_publish, REQUIRED
        )

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


class TestSubscriberWithoutTheCheck:
    @pytest.fixture(autouse=True)
    def _setup(self, member_profile: Container) -> Iterator[None]:
        gsm: Any = getGlobalSiteManager()
        gsm.registerHandler(activate_without_checking, REQUIRED)
        self.profile = member_profile
        yield
        gsm.unregisterHandler(activate_without_checking, REQUIRED)

    def test_an_unavailable_transition_propagates(self) -> None:
        """The error leaves the subscriber through the transition that fired it."""
        mw_api.transition(
            self.profile, "activate", workflow_id=FOUNDATION_MEMBER_WORKFLOW
        )

        with pytest.raises(InvalidParameterError):
            api.content.transition(obj=self.profile, transition="publish")
