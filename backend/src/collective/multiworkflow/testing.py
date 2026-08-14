"""Test layers and a factory for throwaway workflows.

The layers load the :mod:`collective.multiworkflow.demo` ZCML but do not apply
its profile: it enables the example behavior on Document, which would put an
additional workflow on the very content the "vanilla content is untouched"
tests need left alone. Tests that want the example ask for it with
``@pytest.mark.portal(profiles=[DEMO_PROFILE])``.
"""

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing.zope import WSGI_SERVER_FIXTURE
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from typing import Any

import collective.multiworkflow
import collective.multiworkflow.demo


def add_workflow(
    wftool: Any,
    workflow_id: str,
    state_variable: str,
    states: dict[str, tuple[str, ...]],
    initial_state: str,
    transitions: tuple[tuple[str, str, str], ...],
    permissions: tuple[str, ...] = (),
) -> Any:
    """Create a minimal DCWorkflow definition inside the tool.

    Intended for tests and demos that need a secondary workflow without
    shipping a GenericSetup profile for it. The workflow records no history
    and, unless ``permissions`` says otherwise, manages no permissions.

    :param wftool: the ``portal_workflow`` tool.
    :param workflow_id: id of the workflow to create.
    :param state_variable: the workflow's ``state_var``; never ``review_state``.
    :param states: mapping of state id to the transition ids leaving it.
    :param initial_state: id of the state new objects start in.
    :param transitions: tuples of ``(transition_id, title, new_state_id)``.
    :param permissions: permissions this workflow manages. Keep these disjoint
        from the ones every other workflow in the chain manages, or the two
        will overwrite each other's role mappings.
    :returns: the created workflow definition, acquisition-wrapped.
    """
    wftool._setObject(workflow_id, DCWorkflowDefinition(workflow_id))
    workflow = wftool[workflow_id]
    workflow.variables.setStateVar(state_variable)
    workflow.permissions = permissions

    for state_id in states:
        workflow.states.addState(state_id)
    for state_id, leaving in states.items():
        workflow.states[state_id].setProperties(title=state_id, transitions=leaving)
    workflow.states.setInitialState(initial_state)

    for transition_id, title, new_state_id in transitions:
        workflow.transitions.addTransition(transition_id)
        workflow.transitions[transition_id].setProperties(
            title=title,
            new_state_id=new_state_id,
            trigger_type=TRIGGER_USER_ACTION,
            actbox_name=title,
            actbox_url="",
            props={"guard_permissions": ""},
        )
    return workflow


class Layer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer. plone.restapi and plone.volto come in through the package's
        # own dependencies.zcml.
        # meta first: the demo package's configure.zcml uses the
        # <plone:additionalworkflows /> directive, and autoinclude — which
        # loads meta.zcml in a real site — is switched off in this fixture.
        self.loadZCML(name="meta.zcml", package=collective.multiworkflow)
        self.loadZCML(package=collective.multiworkflow)
        self.loadZCML(package=collective.multiworkflow.demo)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.multiworkflow:default")
        # The example behavior, so tests never have to apply it themselves. It
        # only touches the Profile type it also introduces, so every stock type
        # stays exactly as Plone configured it.
        #
        # Its sibling ``:content`` profile is deliberately NOT applied: the
        # importer behind it commits, which an integration layer's per-test
        # ``transaction.abort()`` cannot undo.
        applyProfile(portal, "collective.multiworkflow.demo:demo")


FIXTURE = Layer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="Collective.MultiworkflowLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, WSGI_SERVER_FIXTURE),
    name="Collective.MultiworkflowLayer:FunctionalTesting",
)


ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        WSGI_SERVER_FIXTURE,
    ),
    name="Collective.MultiworkflowLayer:AcceptanceTesting",
)
