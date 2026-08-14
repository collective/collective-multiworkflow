"""Layers, and the fixtures every subpackage shares.

A fixture belongs here once more than one subpackage wants the *same* one.
Fixtures that merely share a name across subpackages — ``membership_workflow``
builds a different workflow in each — stay local, next to the assertions that
depend on their exact shape.
"""

from collections.abc import Iterator
from collective.multiworkflow.declaration import contributes
from collective.multiworkflow.interfaces import IAdditionalWorkflowsFor
from collective.multiworkflow.testing import ACCEPTANCE_TESTING
from collective.multiworkflow.testing import add_workflow
from collective.multiworkflow.testing import FUNCTIONAL_TESTING
from collective.multiworkflow.testing import INTEGRATION_TESTING
from plone import api
from plone.base.interfaces import IWorkflowChain
from plone.dexterity.content import Container
from Products.CMFCore.interfaces import IWorkflowTool
from Products.CMFPlone.workflow import ToolWorkflowChain
from pytest_plone import fixtures_factory
from tests import IExtraWorkflows
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from tests import SPIKE_COLLIDING_STATE_VAR
from tests import SPIKE_COLLIDING_WORKFLOW
from tests import SPIKE_STATE_VAR
from tests import SPIKE_WORKFLOW
from typing import Any
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.interface import alsoProvides
from zope.interface import implementer

import pytest


pytest_plugins = ["pytest_plone"]


globals().update(
    fixtures_factory((
        (ACCEPTANCE_TESTING, "acceptance"),
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


@pytest.fixture()
def wftool(portal: Any) -> Any:
    """The ``portal_workflow`` tool."""
    return api.portal.get_tool("portal_workflow")


@pytest.fixture()
def catalog(portal: Any) -> Any:
    """The ``portal_catalog`` tool."""
    return api.portal.get_tool("portal_catalog")


@pytest.fixture()
def member_profile(portal: Any) -> Container:
    """The participating content the ``portal`` marker created."""
    return portal[MEMBER_PROFILE["id"]]


@pytest.fixture()
def plain_document(portal: Any) -> Container:
    """The non-participating content the ``portal`` marker created."""
    return portal[PLAIN_DOCUMENT["id"]]


@pytest.fixture()
def register_contribution() -> Iterator[Any]:
    """Register contribution subscribers, unregistering them afterwards."""
    registered: list[Any] = []
    gsm = getGlobalSiteManager()

    def _register(marker: Any, *workflow_ids: str) -> Any:
        factory = contributes(marker, *workflow_ids)
        gsm.registerSubscriptionAdapter(factory, (marker,), IAdditionalWorkflowsFor)
        registered.append((factory, marker))
        return factory

    yield _register

    for factory, marker in registered:
        gsm.unregisterSubscriptionAdapter(factory, (marker,), IAdditionalWorkflowsFor)


# --- Spike scaffolding -------------------------------------------------------
#
# Only the ``test_spike_*`` modules use these. They deliberately reimplement in
# miniature what this package ships, so that a spike failing means Plone changed
# rather than that our code broke. See ``tests/__init__.py``.


@pytest.fixture()
def spike_workflow(wftool: Any) -> Any:
    """A secondary state-tracking workflow with a distinct ``state_var``."""
    return add_workflow(
        wftool,
        SPIKE_WORKFLOW,
        SPIKE_STATE_VAR,
        states={
            "pending": ("activate",),
            "active": ("lapse",),
            "lapsed": ("activate",),
        },
        initial_state="pending",
        transitions=(
            ("activate", "Activate", "active"),
            ("lapse", "Lapse", "lapsed"),
        ),
    )


@pytest.fixture()
def spike_colliding_workflow(wftool: Any) -> Any:
    """A secondary workflow reusing ``publish``, a core transition id."""
    return add_workflow(
        wftool,
        SPIKE_COLLIDING_WORKFLOW,
        SPIKE_COLLIDING_STATE_VAR,
        states={"unset": ("publish",), "flagged": ()},
        initial_state="unset",
        transitions=(("publish", "Publish (collision)", "flagged"),),
    )


@pytest.fixture()
def spike_participant(plain_document: Any) -> Any:
    """A Document marked as participating, via the spikes' own marker."""
    alsoProvides(plain_document, IExtraWorkflows)
    return plain_document


@pytest.fixture()
def spike_chain_adapter() -> Iterator[Any]:
    """Register an appending chain adapter, and unregister it afterwards.

    The yielded callable takes the workflow ids to contribute and installs an
    adapter more specific than Plone's default ``ToolWorkflowChain`` — the same
    shape as ``collective.multiworkflow.chain``, written out here so the spikes
    never depend on it.
    """
    registered: list[Any] = []
    gsm = getGlobalSiteManager()

    def _register(*workflow_ids: str) -> Any:
        @adapter(IExtraWorkflows, IWorkflowTool)
        @implementer(IWorkflowChain)
        def extra_workflow_chain(context: Any, tool: Any) -> tuple[str, ...]:
            # Calling the default adapter *function* directly is the point of
            # this scaffolding: it reads ``tool._chains_by_type`` and never
            # re-enters ``getChainFor``, so there is no recursion to guard.
            base = tuple(ToolWorkflowChain(context, tool))
            extra = tuple(
                wf_id
                for wf_id in workflow_ids
                if wf_id not in base and tool.getWorkflowById(wf_id) is not None
            )
            return base + extra

        gsm.registerAdapter(extra_workflow_chain)
        registered.append(extra_workflow_chain)
        return extra_workflow_chain

    yield _register

    for factory in registered:
        gsm.unregisterAdapter(factory)
