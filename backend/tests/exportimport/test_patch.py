"""The patch is installed, and it keeps imported content correctly indexed."""

from . import IMPORTED_STATES
from . import STALE_MEMBERSHIP_STATE
from collective.multiworkflow import api as mw_api
from collective.multiworkflow import exportimport
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


class TestPatchInstallation:
    """The wrapper is in place, once, and reachable where it is read."""

    def test_updater_is_patched(self) -> None:
        """Loading the package's ZCML replaced the updater."""
        assert (
            getattr(import_helpers.update_workflow_history, "patched_by", None)
            == exportimport.__name__
        )

    def test_updaters_list_sees_the_patch(self) -> None:
        """``updaters()`` reads the module global, so it picks the wrapper up.

        This is what makes a module-attribute patch sufficient: no reference to
        the original survives anywhere the importer looks.
        """
        names = {updater.name: updater.func for updater in import_helpers.updaters()}

        assert names["update_workflow_history"] is (
            import_helpers.update_workflow_history
        )

    def test_patch_is_idempotent(self) -> None:
        """Applying it twice does not wrap the wrapper."""
        patched = import_helpers.update_workflow_history

        exportimport.apply_patches()

        assert import_helpers.update_workflow_history is patched

    def test_docstring_is_preserved(self) -> None:
        """The updater's description is what the importer logs."""
        assert import_helpers.update_workflow_history.__doc__


class TestImportedContentIsIndexed:
    """The bug the patch exists for, asserted on real imported content.

    Functional rather than integration: the importer commits as it goes, which
    an integration layer's per-test rollback cannot undo.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, functional_portal: Any) -> None:
        applyProfile(functional_portal, CONTENT_PROFILE)
        flush_indexing()
        self.portal = functional_portal
        self.item = functional_portal[EXAMPLE_DOCUMENT][EXAMPLE_PROFILE_ITEM]

    def test_object_carries_the_imported_states(self) -> None:
        """The premise: the import really did restore both workflows."""
        assert mw_api.get_states(self.item) == IMPORTED_STATES

    @pytest.mark.parametrize(
        "workflow_id,state_id",
        list(IMPORTED_STATES.items()),
    )
    def test_index_finds_the_imported_item(
        self, workflow_id: str, state_id: str
    ) -> None:
        """Both workflows' imported states are queryable.

        Asserting on a query rather than on a brain is deliberate: ZCatalog
        rebuilds every metadata column on a partial reindex, so a brain can
        carry the right value while the index that should have found it is
        stale.
        """
        results = api.content.find(**{
            WORKFLOW_STATES: format_state(workflow_id, state_id)
        })

        assert EXAMPLE_PROFILE_ITEM in [brain.getId for brain in results]

    def test_stale_membership_state_is_not_indexed(self) -> None:
        """The failure mode itself: the initial state must not be found.

        Without the patch this query returns the item, because the index still
        holds the state the object was catalogued in before its history was
        restored.
        """
        results = api.content.find(**{
            WORKFLOW_STATES: format_state(
                FOUNDATION_MEMBER_WORKFLOW, STALE_MEMBERSHIP_STATE
            )
        })

        assert EXAMPLE_PROFILE_ITEM not in [brain.getId for brain in results]
