import pytest


@pytest.fixture(scope="class")
def portal(portal_class):
    """Return the portal object."""
    yield portal_class


@pytest.fixture(scope="class")
def http_request(integration_class):
    """Return the HTTP request object."""
    yield integration_class["request"]
