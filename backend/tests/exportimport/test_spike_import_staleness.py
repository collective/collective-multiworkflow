"""How `plone.exportimport` behaves *without* our patch.

A spike, in this suite's sense: it asserts upstream's behavior, not ours. It
exists for two reasons.

- It proves the patch is load-bearing. Without it, the tests in
  ``test_patch.py`` would pass whether or not the wrapper did anything.
- It is the signal to delete the patch. When `plone.exportimport` fixes this,
  this module fails, and that failure means the wrapper can go — not that
  something broke.

It reaches the unpatched function through ``__wrapped__`` rather than by
unloading the ZCML, so nothing global is left mutated if it fails midway.
"""

from . import MANAGE_MEMBERSHIP
from . import PENDING_ROLES
from . import roles_with
from . import STALE_MEMBERSHIP_STATE
from collective.multiworkflow import api as mw_api
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.utils.workflow import format_state
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from plone import api
from plone.app.testing import applyProfile
from plone.exportimport.utils.content import import_helpers
from tests import flush_indexing
from tests.demo import CONTENT_PROFILE
from tests.demo import EXAMPLE_DOCUMENT
from tests.demo import EXAMPLE_PROFILE_ITEM
from typing import Any

import pytest


class TestUnpatchedImportLeavesTheIndexStale:
    @pytest.fixture(autouse=True)
    def _setup(self, functional_portal: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        """Import the example content with the updater unwrapped."""
        monkeypatch.setattr(
            import_helpers,
            "update_workflow_history",
            import_helpers.update_workflow_history.__wrapped__,
        )
        applyProfile(functional_portal, CONTENT_PROFILE)
        flush_indexing()
        self.item = functional_portal[EXAMPLE_DOCUMENT][EXAMPLE_PROFILE_ITEM]

    def test_object_state_is_restored(self) -> None:
        """Upstream restores the object correctly. The object is never wrong."""
        assert (
            mw_api.get_state(self.item, workflow_id=FOUNDATION_MEMBER_WORKFLOW)
            == "active"
        )

    def test_index_holds_the_state_before_the_import(self) -> None:
        """Only the catalog is wrong, and it is wrong silently.

        The item is still found under the state it was created in, which is
        the whole bug: a query for pending memberships returns an active one.
        """
        results = api.content.find(**{
            WORKFLOW_STATES: format_state(
                FOUNDATION_MEMBER_WORKFLOW, STALE_MEMBERSHIP_STATE
            )
        })

        assert EXAMPLE_PROFILE_ITEM in [brain.getId for brain in results]

    def test_publication_state_is_indexed_correctly(self) -> None:
        """Why the bug hides: ``review_state`` is fresh either way.

        ``update_review_state`` runs a real transition just before the history
        is assigned, so the publication half of the same index is correct and
        a spot-check of imported content looks healthy.
        """
        results = api.content.find(**{
            WORKFLOW_STATES: format_state("simple_publication_workflow", "published")
        })

        assert EXAMPLE_PROFILE_ITEM in [brain.getId for brain in results]

    def test_role_mappings_are_the_initial_states(self) -> None:
        """Issue #6: the security is as stale as the index, and as silent.

        The object is ``active``, but its permission map is still the one
        ``pending`` defines, because no transition ever applied the new one.
        """
        assert roles_with(self.item, MANAGE_MEMBERSHIP) == PENDING_ROLES
