"""Spike: does `plone.restapi`'s content serialization carry ``workflow_states``?

It does not, which is why ``collective.multiworkflow.restapi.serializer.dxcontent``
patches it in. The spike calls the original method through ``__wrapped__``, so
it observes `plone.restapi` alone. When it fails, upstream has started returning
the key, and the patch can go.
"""

from plone.restapi.serializer.dxcontent import SerializeToJson
from tests import PLAIN_DOCUMENT
from typing import Any

import pytest


#: Spikes assert Plone's own behaviour, so they carry the ``spike`` marker and
#: can be deselected with ``-m "not spike"``.
pytestmark = [
    pytest.mark.spike,
    pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"]),
]


def test_upstream_payload_has_no_workflow_states(
    portal: Any, http_request: Any
) -> None:
    """Upstream serializes ``review_state`` only."""
    serializer = SerializeToJson(portal[PLAIN_DOCUMENT["id"]], http_request)

    result = SerializeToJson.__call__.__wrapped__(serializer)

    assert "review_state" in result
    assert "workflow_states" not in result
