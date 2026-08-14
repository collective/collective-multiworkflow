"""Tests for permission composition and the audit helper.

Two things are asserted here, and they are the reason the package documents a
*disjoint sets* rule rather than a *no permissions* one: disjoint sets genuinely
compose, and an overlap genuinely loses one workflow's mapping.
"""

from . import CLASHING_WORKFLOW
from . import MEMBERSHIP_PERMISSION
from . import MEMBERSHIP_WORKFLOW
from . import SHARED_PERMISSION
from collective.multiworkflow import api as mwapi
from plone import api
from plone.dexterity.content import Container
from Products.CMFPlone.WorkflowTool import WorkflowTool
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
from tests import roles_for

import pytest


pytestmark = pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])


class TestConflictingPermissions:
    """The three documents here are one object in three states.

    ``member_document`` and ``clashing_document`` both mark ``plain_document``
    in place, so only the unmarked one can be bound in ``_setup``; the marked
    variants stay parameters, one per test that wants them.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, plain_document: Container) -> None:
        self.plain_document = plain_document

    def test_vanilla_content_has_no_conflict(self) -> None:
        """A single-workflow chain cannot conflict with itself."""
        assert mwapi.conflicting_permissions(self.plain_document) == {}

    def test_disjoint_chain_has_no_conflict(self, member_document: Container) -> None:
        """Two workflows managing different permissions compose cleanly."""
        assert mwapi.conflicting_permissions(member_document) == {}

    def test_overlap_is_reported(self, clashing_document: Container) -> None:
        """A permission claimed twice is named, with both claimants."""
        assert mwapi.conflicting_permissions(clashing_document) == {
            SHARED_PERMISSION: [PUBLICATION_WORKFLOW, CLASHING_WORKFLOW]
        }

    def test_claimants_are_listed_in_chain_order(
        self, clashing_document: Container
    ) -> None:
        """Order matters: it is the order the mappings are applied in."""
        claimants = mwapi.conflicting_permissions(clashing_document)[SHARED_PERMISSION]

        assert claimants[0] == PUBLICATION_WORKFLOW

    def test_only_shared_permissions_are_reported(
        self, clashing_document: Container
    ) -> None:
        """Permissions with a single claimant are not noise in the report."""
        conflicts = mwapi.conflicting_permissions(clashing_document)

        assert "View" not in conflicts


class TestDisjointSetsCompose:
    """The guarantee the documented rule rests on."""

    @pytest.fixture(autouse=True)
    def _setup(self, member_document: Container) -> None:
        self.document = member_document

    def test_secondary_mapping_is_applied(self) -> None:
        """The additional workflow writes its own permission on creation."""
        assert roles_for(self.document, MEMBERSHIP_PERMISSION) == ("Manager",)

    def test_publication_does_not_disturb_it(self) -> None:
        """A publication transition rewrites only publication's permissions."""
        api.content.transition(obj=self.document, transition="publish")

        assert roles_for(self.document, MEMBERSHIP_PERMISSION) == ("Manager",)

    def test_secondary_does_not_disturb_publication(self) -> None:
        """And the additional workflow rewrites only its own."""
        api.content.transition(obj=self.document, transition="publish")
        before = roles_for(self.document, SHARED_PERMISSION)

        mwapi.transition(
            self.document, transition="activate", workflow_id=MEMBERSHIP_WORKFLOW
        )

        assert roles_for(self.document, SHARED_PERMISSION) == before


class TestOverlapLosesAMapping:
    """The hazard the audit helper exists to surface."""

    @pytest.fixture(autouse=True)
    def _setup(self, clashing_document: Container, wftool: WorkflowTool) -> None:
        self.document = clashing_document
        self.wftool = wftool

    def test_secondary_transition_overwrites_publication(self) -> None:
        """Publication's mapping survives only until the other one moves."""
        api.content.transition(obj=self.document, transition="publish")
        published = roles_for(self.document, SHARED_PERMISSION)
        assert "Editor" in published

        mwapi.transition(
            self.document, transition="activate", workflow_id=CLASHING_WORKFLOW
        )

        assert roles_for(self.document, SHARED_PERMISSION) == ("Manager",)

    def test_update_role_mappings_restores_chain_order(self) -> None:
        """Reapplying the whole chain hands the permission back to the last."""
        api.content.transition(obj=self.document, transition="publish")

        self.wftool.updateRoleMappings()

        # Chain order decides: the conflicting workflow is appended, so it
        # writes last and wins.
        assert roles_for(self.document, SHARED_PERMISSION) == ("Manager",)
