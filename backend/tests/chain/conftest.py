"""Fixtures for the workflow chain mechanism tests.

Only what is specific to this package: the workflows it builds and the marker
it applies. ``wftool``, ``plain_document`` and ``register_contribution`` come
from the suite-wide ``conftest`` one level up.
"""

from . import IMember
from . import MEMBERSHIP_STATE_VAR
from . import MEMBERSHIP_WORKFLOW
from . import REVIEW_STATE_VAR
from . import REVIEW_WORKFLOW
from collective.multiworkflow.testing import add_workflow
from typing import Any
from zope.interface import alsoProvides

import pytest


@pytest.fixture()
def membership_workflow(wftool: Any) -> Any:
    """A secondary state-tracking workflow."""
    return add_workflow(
        wftool,
        MEMBERSHIP_WORKFLOW,
        MEMBERSHIP_STATE_VAR,
        states={"pending": ("activate",), "active": ("lapse",), "lapsed": ()},
        initial_state="pending",
        transitions=(
            ("activate", "Activate", "active"),
            ("lapse", "Lapse", "lapsed"),
        ),
    )


@pytest.fixture()
def review_workflow(wftool: Any) -> Any:
    """A second secondary workflow, with its own state variable."""
    return add_workflow(
        wftool,
        REVIEW_WORKFLOW,
        REVIEW_STATE_VAR,
        states={"unreviewed": ("approve",), "approved": ()},
        initial_state="unreviewed",
        transitions=(("approve", "Approve", "approved"),),
    )


@pytest.fixture()
def member_document(plain_document: Any) -> Any:
    """A Document providing *this* package's ``IMember`` marker.

    ``tests.permissions`` has a same-named fixture and a same-named marker, but
    they are a different interface and a different workflow — hence two local
    fixtures rather than one shared.
    """
    alsoProvides(plain_document, IMember)
    return plain_document
