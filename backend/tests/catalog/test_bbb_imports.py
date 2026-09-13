"""The catalog helpers stay importable from the module they used to live in.

The value helpers moved to :mod:`collective.multiworkflow.utils.workflow`, and
the subscriber keeping the index fresh to
:mod:`collective.multiworkflow.subscribers.reindex`.
``collective.multiworkflow.indexers`` re-exports them, so code written against
1.0.0a1, whose documentation imported them from there, keeps working.
"""

from collective.multiworkflow import indexers
from collective.multiworkflow.subscribers import reindex
from collective.multiworkflow.utils import workflow
from types import ModuleType

import pytest


@pytest.mark.parametrize(
    "name",
    ["WORKFLOW_STATES", "STATE_SEPARATOR", "format_state", "parse_state"],
)
def test_reexported(name: str) -> None:
    """The old import path yields the very same object as the new one."""
    assert getattr(indexers, name) is getattr(workflow, name)


def test_subscriber_reexported() -> None:
    """``reindex_workflow_states`` is the very function the subscriber module holds."""
    from collective.multiworkflow.indexers import reindex_workflow_states

    assert reindex_workflow_states is reindex.reindex_workflow_states


def test_indexer_submodule_is_not_shadowed() -> None:
    """``indexers.workflow_states`` is still the module ZCML registers from.

    Re-exporting the indexer function under the same name would replace the
    submodule attribute, and the factory ``.workflow_states.workflow_states``
    would no longer resolve.
    """
    from collective.multiworkflow.indexers import workflow_states

    assert isinstance(workflow_states, ModuleType)
