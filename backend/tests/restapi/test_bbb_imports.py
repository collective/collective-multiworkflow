"""The REST API classes stay importable from the modules they used to live in.

In 1.0.0a1, ``restapi/serializer.py``, ``restapi/service.py`` and
``restapi/history.py`` held them. They moved to the ``restapi.serializer`` and
``restapi.services`` subpackages, and the old locations re-export them.
"""

from collective.multiworkflow.restapi.serializer import workflow
from collective.multiworkflow.restapi.services.history import get as history_get
from collective.multiworkflow.restapi.services.workflow import get as workflow_get

import pytest


def test_serializer_reexported() -> None:
    """``WorkflowChainInfo`` is the very class the ``workflow`` module holds."""
    from collective.multiworkflow.restapi.serializer import WorkflowChainInfo

    assert WorkflowChainInfo is workflow.WorkflowChainInfo


def test_service_reexported() -> None:
    """``WorkflowChainInfoService`` is the very class the service module holds."""
    from collective.multiworkflow.restapi.service import WorkflowChainInfoService

    assert WorkflowChainInfoService is workflow_get.WorkflowChainInfoService


@pytest.mark.parametrize("name", ["ChainHistoryGet", "ChainHistoryViewlet"])
def test_history_reexported(name: str) -> None:
    """The history classes are the very ones the service module holds."""
    from collective.multiworkflow.restapi import history

    assert getattr(history, name) is getattr(history_get, name)
