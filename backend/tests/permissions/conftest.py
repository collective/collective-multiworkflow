"""Fixtures for the permission composition tests.

The workflows here are built programmatically rather than shipped as a profile:
the point is to compose *arbitrary* permission sets, including the conflicting
one no shipped profile should ever contain. ``wftool``, ``plain_document`` and
``register_contribution`` come from the suite-wide ``conftest`` one level up.
"""

from . import CLASHING_STATE_VAR
from . import CLASHING_WORKFLOW
from . import IClashing
from . import IMember
from . import MEMBERSHIP_PERMISSION
from . import MEMBERSHIP_STATE_VAR
from . import MEMBERSHIP_WORKFLOW
from . import SHARED_PERMISSION
from collective.multiworkflow.testing import add_workflow
from typing import Any
from zope.interface import alsoProvides

import pytest


#: Every workflow below shares this shape; only the permissions differ.
STATES = {"pending": ("activate",), "active": ()}
TRANSITIONS = (("activate", "Activate", "active"),)


@pytest.fixture()
def membership_workflow(wftool: Any) -> Any:
    """A secondary workflow managing a permission no other workflow claims."""
    workflow = add_workflow(
        wftool,
        MEMBERSHIP_WORKFLOW,
        MEMBERSHIP_STATE_VAR,
        states=STATES,
        initial_state="pending",
        transitions=TRANSITIONS,
        permissions=(MEMBERSHIP_PERMISSION,),
    )
    workflow.states["pending"].setPermission(MEMBERSHIP_PERMISSION, 0, ("Manager",))
    workflow.states["active"].setPermission(
        MEMBERSHIP_PERMISSION, 0, ("Manager", "Owner")
    )
    return workflow


@pytest.fixture()
def clashing_workflow(wftool: Any) -> Any:
    """A secondary workflow claiming a permission publication also manages."""
    workflow = add_workflow(
        wftool,
        CLASHING_WORKFLOW,
        CLASHING_STATE_VAR,
        states=STATES,
        initial_state="pending",
        transitions=TRANSITIONS,
        permissions=(SHARED_PERMISSION,),
    )
    for state_id in STATES:
        workflow.states[state_id].setPermission(SHARED_PERMISSION, 0, ("Manager",))
    return workflow


@pytest.fixture()
def member_document(
    plain_document: Any,
    membership_workflow: Any,
    register_contribution: Any,
    wftool: Any,
) -> Any:
    """A Document whose chain gains the disjoint workflow.

    Same name as ``tests.chain``'s fixture, deliberately not shared: the marker
    it applies is this package's own interface, and the workflow behind it
    manages permissions the other one does not.
    """
    register_contribution(IMember, MEMBERSHIP_WORKFLOW)
    alsoProvides(plain_document, IMember)
    # The chain changed after creation, so the new workflow has to be told the
    # object exists before it has a state or a role mapping.
    wftool.notifyCreated(plain_document)
    return plain_document


@pytest.fixture()
def clashing_document(
    plain_document: Any,
    clashing_workflow: Any,
    register_contribution: Any,
    wftool: Any,
) -> Any:
    """A Document whose chain gains the conflicting workflow."""
    register_contribution(IClashing, CLASHING_WORKFLOW)
    alsoProvides(plain_document, IClashing)
    wftool.notifyCreated(plain_document)
    return plain_document
