"""Fixtures for the ``workflow_states`` index tests.

Only what is specific to this package. ``wftool``, ``catalog``,
``plain_document`` and ``register_contribution`` come from the suite-wide
``conftest`` one level up.
"""

from . import AUDIT_STATE_VAR
from . import AUDIT_WORKFLOW
from . import IAudited
from collective.multiworkflow.testing import add_workflow
from tests import flush_indexing
from typing import Any
from zope.interface import alsoProvides

import pytest


@pytest.fixture()
def audit_workflow(wftool: Any) -> Any:
    """A secondary workflow keeping a state variable of its own."""
    return add_workflow(
        wftool,
        AUDIT_WORKFLOW,
        AUDIT_STATE_VAR,
        states={"unaudited": ("audit",), "audited": ()},
        initial_state="unaudited",
        transitions=(("audit", "Audit", "audited"),),
    )


@pytest.fixture()
def audited_document(
    plain_document: Any, audit_workflow: Any, register_contribution: Any
) -> Any:
    """A Document that joined the audit workflow *after* being catalogued.

    Marking existing content is how a real site adopts a behavior, and it means
    the object's indexed value predates the contribution — so the fixture
    reindexes, exactly as an upgrade step would.

    The flush is what makes the tests that follow mean anything, and it took a
    mutation run to notice. Left queued, that reindex is still pending when a
    test transitions the object; the first query then drains it against the
    *post-transition* object and writes correct values, hiding the very
    staleness the subscriber exists to prevent. An upgrade step commits before
    anyone transitions anything, so flushing here is also the truthful
    sequence.
    """
    register_contribution(IAudited, AUDIT_WORKFLOW)
    alsoProvides(plain_document, IAudited)
    plain_document.reindexObject()
    flush_indexing()
    return plain_document
