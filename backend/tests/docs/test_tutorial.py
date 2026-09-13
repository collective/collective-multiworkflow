"""``tutorials/add-a-second-workflow.md``, followed step by step.

The tutorial's workflow definition and ZCML are held here verbatim and reach
the site the way they would from a real add-on: the definition through
:func:`tests.docs.load_definition`, the ZCML through ``xmlconfig`` against
``tests.docs.tutorial``, which stands in for ``my.package``.

``how-to-guides/write-a-composing-workflow.md`` shows fragments of the same
workflow, so its samples are asserted here as well: each fragment must be a
slice of the tutorial's definition, which the steps below prove imports and
works.
"""

from . import load_definition
from .tutorial.interfaces import IMember
from collections.abc import Iterator
from collective.multiworkflow import api as mw_api
from collective.multiworkflow.declaration import workflow_label
from collective.multiworkflow.interfaces import IAdditionalWorkflowLabel
from collective.multiworkflow.interfaces import IAdditionalWorkflowsFor
from collective.multiworkflow.utils.workflow import format_state
from plone import api
from plone.behavior.interfaces import IBehavior
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from typing import Any
from zope.component import getGlobalSiteManager
from zope.component.hooks import getSite
from zope.component.hooks import setSite
from zope.configuration import xmlconfig

import collective.multiworkflow
import plone.behavior
import pytest
import tests.docs.tutorial
import textwrap


pytestmark = pytest.mark.portal(roles=["Manager"])

WORKFLOW_ID = "membership_workflow"
BEHAVIOR = "my.package.member"

#: Step 2: ``profiles/default/workflows/membership_workflow/definition.xml``.
DEFINITION = """\
<?xml version="1.0" encoding="utf-8"?>
<dc-workflow
    workflow_id="membership_workflow"
    title="Membership"
    state_variable="workflow_states"
    initial_state="pending"
    >

  <state state_id="pending" title="Pending">
    <exit-transition transition_id="membership_activate" />
  </state>

  <state state_id="active" title="Active">
    <exit-transition transition_id="membership_lapse" />
  </state>

  <state state_id="lapsed" title="Lapsed">
    <exit-transition transition_id="membership_activate" />
  </state>

  <transition transition_id="membership_activate"
              title="Activate membership"
              new_state="active"
              trigger="USER"
              before_script=""
              after_script=""
              >
    <action category="workflow"
            url="%(content_url)s/content_status_modify?workflow_action=membership_activate"
            >Activate membership</action>
    <guard>
      <guard-permission>Modify portal content</guard-permission>
    </guard>
  </transition>

  <transition transition_id="membership_lapse"
              title="Lapse membership"
              new_state="lapsed"
              trigger="USER"
              before_script=""
              after_script=""
              >
    <action category="workflow"
            url="%(content_url)s/content_status_modify?workflow_action=membership_lapse"
            >Lapse membership</action>
    <guard>
      <guard-permission>Modify portal content</guard-permission>
    </guard>
  </transition>

</dc-workflow>
"""

#: Step 3: ``configure.zcml``.
CONFIGURE_ZCML = """\
<configure
    xmlns:plone="http://namespaces.plone.org/plone"
    i18n_domain="my.package"
    >

  <plone:behavior
      name="my.package.member"
      title="Member"
      description="Track a membership lifecycle alongside publication."
      provides=".interfaces.IMember"
      />

  <plone:additionalworkflows
      marker=".interfaces.IMember"
      workflows="membership_workflow"
      label="Membership status"
      />

</configure>
"""

#: The composing guide's step 1.
COMPOSING_DC_WORKFLOW = """\
<dc-workflow
    workflow_id="membership_workflow"
    title="Membership"
    state_variable="workflow_states"
    initial_state="pending"
    >
"""

#: The composing guide's step 2.
COMPOSING_TRANSITION = """\
<transition transition_id="membership_activate"
            title="Activate membership"
            new_state="active"
            trigger="USER"
            before_script=""
            after_script=""
            >
  <action category="workflow"
          url="%(content_url)s/content_status_modify?workflow_action=membership_activate"
          >Activate membership</action>
  <guard>
    <guard-permission>Modify portal content</guard-permission>
  </guard>
</transition>
"""

#: The query step 6 runs twice.
PUBLISHED_AND_ACTIVE = {
    "query": [
        format_state("simple_publication_workflow", "published"),
        format_state("membership_workflow", "active"),
    ],
    "operator": "and",
}


@pytest.fixture()
def membership_workflow(wftool: Any) -> Any:
    """Step 2: the workflow, installed from the tutorial's definition."""
    wftool._setObject(WORKFLOW_ID, DCWorkflowDefinition(WORKFLOW_ID))
    workflow = wftool[WORKFLOW_ID]
    load_definition(workflow, DEFINITION)
    return workflow


@pytest.fixture()
def tutorial_zcml(portal: Any) -> Iterator[None]:
    """Step 3: the tutorial's ZCML, read as a restart would read it."""
    context = xmlconfig.file("meta.zcml", plone.behavior)
    xmlconfig.file("meta.zcml", collective.multiworkflow, context=context)
    context.package = tests.docs.tutorial
    # Directives register into whatever getSiteManager() returns. With the
    # portal as the active site that is the portal's persistent registry, so
    # step out of it while the ZCML is read.
    site = getSite()
    # arg-type: the stubs demand a site, but None is how zope.component clears
    # the active one.
    setSite(None)  # type: ignore[arg-type]
    try:
        xmlconfig.string(CONFIGURE_ZCML, context=context)
    finally:
        setSite(site)
    yield
    # The global registry is typed as the lookup interface, which does not
    # declare the registration methods it implements.
    gsm: Any = getGlobalSiteManager()
    # Each False would mean a registration landed somewhere this teardown
    # cannot see, and leaked into the tests that follow.
    assert gsm.unregisterUtility(provided=IBehavior, name=BEHAVIOR)
    assert gsm.unregisterUtility(provided=IBehavior, name=IMember.__identifier__)
    assert gsm.unregisterSubscriptionAdapter(
        required=(IMember,), provided=IAdditionalWorkflowsFor
    )
    assert gsm.unregisterUtility(provided=IAdditionalWorkflowLabel, name=WORKFLOW_ID)


class TestTutorial:
    @pytest.fixture(autouse=True)
    def _setup(
        self, portal: Any, wftool: Any, membership_workflow: Any, tutorial_zcml: None
    ) -> None:
        self.portal = portal
        self.wftool = wftool
        self.workflow = membership_workflow

    def enable_the_behavior(self) -> None:
        """Step 4: enable **Member** on the Document type."""
        fti = api.portal.get_tool("portal_types")["Document"]
        fti.manage_changeProperties(behaviors=[*fti.behaviors, BEHAVIOR])

    def create_member_document(self) -> Any:
        self.enable_the_behavior()
        return api.content.create(
            container=self.portal, type="Document", title="A Member Document"
        )

    def test_step_1_a_chain_of_one(self) -> None:
        doc = api.content.create(
            container=self.portal, type="Document", title="A Document"
        )

        assert self.wftool.getChainFor(doc) == ("simple_publication_workflow",)

    def test_step_2_the_definition_imports(self) -> None:
        workflow = self.workflow

        assert workflow.state_var == "workflow_states"
        assert workflow.initial_state == "pending"
        assert sorted(workflow.states.objectIds()) == ["active", "lapsed", "pending"]
        assert sorted(workflow.transitions.objectIds()) == [
            "membership_activate",
            "membership_lapse",
        ]

    def test_step_3_the_label_names_the_workflow(self) -> None:
        assert workflow_label(self.workflow) == "Membership status"

    def test_step_4_a_new_document_has_two_workflows(self) -> None:
        doc = self.create_member_document()

        assert self.wftool.getChainFor(doc) == (
            "simple_publication_workflow",
            "membership_workflow",
        )

    def test_step_5_the_transition_is_offered(self) -> None:
        """The ``<action>`` element is what lists a transition for a user."""
        doc = self.create_member_document()

        assert mw_api.transitions(doc)["membership_workflow"] == ["membership_activate"]

    def test_step_5_transition_the_membership_workflow(self) -> None:
        doc = self.create_member_document()

        assert mw_api.get_states(doc) == {
            "simple_publication_workflow": "private",
            "membership_workflow": "pending",
        }

        mw_api.transition(doc, "membership_activate", workflow_id="membership_workflow")

        assert mw_api.get_states(doc) == {
            "simple_publication_workflow": "private",
            "membership_workflow": "active",
        }
        assert api.content.get_state(doc) == "private"

    def test_step_6_find_the_document_by_its_membership_state(self) -> None:
        doc = self.create_member_document()
        mw_api.transition(doc, "membership_activate", workflow_id="membership_workflow")

        results = api.content.find(
            workflow_states=format_state("membership_workflow", "active")
        )
        assert [brain.Title for brain in results] == ["A Member Document"]

        results = api.content.find(workflow_states=PUBLISHED_AND_ACTIVE)
        assert [brain.Title for brain in results] == []

        api.content.transition(doc, "publish")
        results = api.content.find(workflow_states=PUBLISHED_AND_ACTIVE)
        assert [brain.Title for brain in results] == ["A Member Document"]


class TestWriteAComposingWorkflow:
    def test_the_fragments_are_slices_of_the_tutorial_definition(self) -> None:
        assert COMPOSING_DC_WORKFLOW in DEFINITION
        assert textwrap.indent(COMPOSING_TRANSITION, "  ") in DEFINITION

    def test_verify_the_composition(
        self,
        portal: Any,
        membership_workflow: Any,
        tutorial_zcml: None,
    ) -> None:
        fti = api.portal.get_tool("portal_types")["Document"]
        fti.manage_changeProperties(behaviors=[*fti.behaviors, BEHAVIOR])
        obj = api.content.create(container=portal, type="Document", title="A Member")

        assert mw_api.conflicting_permissions(obj) == {}

        owners = mw_api.owning_workflow(obj)

        assert owners["membership_activate"] == "membership_workflow"
