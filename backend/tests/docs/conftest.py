"""Fixtures for the documentation examples.

These are functional tests that go over HTTP, so everything hangs off
``functional_portal``. The session deliberately does *not* use the ``++api++``
traverser: the recorded request line is part of the documentation, and a reader
copying it should see the plain content URL with an ``Accept`` header, which is
how ``plone.restapi`` documents every one of its endpoints.
"""

from collections.abc import Iterator
from plone.restapi.tests.statictime import StaticTime
from pytest_plone import _types as t
from typing import Any

import pytest
import transaction


@pytest.fixture()
def docs_session(functional_portal: Any, request_factory: t.RequestFactory) -> Any:
    """A manager session against the portal, with content committed.

    The HTTP requests below run in their own transaction, so content the
    ``@pytest.mark.portal`` marker created is invisible to them — a bare 404 —
    until it is committed.

    :returns: the session the examples are recorded from.
    """
    transaction.commit()
    return request_factory(role="Manager", api=False)


@pytest.fixture(autouse=True)
def static_time() -> Iterator[StaticTime]:
    """Freeze the timestamps that reach a recorded payload.

    Patches the accessors rather than the clock, which is what ``plone.restapi``
    settled on: freezing time outright has broken code that assumes a monotonic
    clock, ZODB's transaction ids above all.

    :returns: the running helper, for a test that wants to read its base times.
    """
    with StaticTime() as helper:
        yield helper
