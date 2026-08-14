"""Fixtures for the ``@workflow`` REST API tests.

These are functional tests: they go over HTTP through the ``++api++``
traverser, so everything hangs off ``functional_portal`` rather than the
integration ``portal``.
"""

from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from typing import Any

import pytest
import transaction


@pytest.fixture()
def committed_portal(functional_portal: Any) -> Any:
    """The functional portal, with the marker's provisioning committed.

    The HTTP requests below run in their own transaction, so content and
    profiles applied by ``@pytest.mark.portal`` are invisible to them — a bare
    404 — until they are committed.
    """
    transaction.commit()
    return functional_portal


@pytest.fixture()
def member_payload(committed_portal: Any, manager_request: Any) -> dict:
    """The ``@workflow`` payload for the participating Profile."""
    response = manager_request.get(f"/{MEMBER_PROFILE['id']}/@workflow")
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture()
def plain_payload(committed_portal: Any, manager_request: Any) -> dict:
    """The ``@workflow`` payload for non-participating content."""
    response = manager_request.get(f"/{PLAIN_DOCUMENT['id']}/@workflow")
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture()
def member_history(committed_portal: Any, manager_request: Any) -> list:
    """The ``@history`` listing for the participating Profile."""
    response = manager_request.get(f"/{MEMBER_PROFILE['id']}/@history")
    assert response.status_code == 200, response.text
    return response.json()


@pytest.fixture()
def plain_history(committed_portal: Any, manager_request: Any) -> list:
    """The ``@history`` listing for non-participating content."""
    response = manager_request.get(f"/{PLAIN_DOCUMENT['id']}/@history")
    assert response.status_code == 200, response.text
    return response.json()
