"""Does content created before the behavior was enabled participate?

**Yes, and ordering does not matter.** Behavior markers are not stamped onto
content at creation: ``DexterityContent.__providedBy__`` is an
``FTIAwareSpecification`` descriptor that recomputes the provided interfaces
from the FTI on access, with a cache keyed on the FTI's modification time.

So enabling a behavior on a type immediately makes every existing object of
that type provide its marker — and therefore participate in the chain. Together
with the initial-state read fallback, this means content that predates the
behavior needs no migration at all.

The "before" case is exercised on **Document**, and has to be: ``Profile``
carries the behavior in its own FTI and is introduced by the same profile, so
no Profile can exist before the behavior applies to it. Enabling the behavior
here is a plain FTI edit rather than a profile import, which is also the
narrower thing to assert — the claim is about the FTI, not about GenericSetup.
"""

from . import FOUNDATION_MEMBER_BEHAVIOR
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.demo.behavior import IFoundationMember
from collective.multiworkflow.indexers import WORKFLOW_STATES
from plone import api
from plone.dexterity.content import Container
from Products.CMFPlone.WorkflowTool import WorkflowTool
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT

import pytest


@pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])
class TestContentCreatedBeforeTheBehavior:
    """Content first, behavior second — still participates."""

    @pytest.fixture(autouse=True)
    def _setup(self, wftool: WorkflowTool, plain_document: Container) -> None:
        """Enable the behavior on Document *after* the content already exists."""
        assert not IFoundationMember.providedBy(plain_document)

        # Through ``manage_changeProperties``, not by assigning to
        # ``fti.behaviors``: only the former fires the modification event that
        # invalidates the schema cache the marker lookup reads from.
        fti = api.portal.get_tool("portal_types")[PLAIN_DOCUMENT["type"]]
        fti.manage_changeProperties(
            behaviors=[*fti.behaviors, FOUNDATION_MEMBER_BEHAVIOR]
        )
        self.wftool = wftool
        self.document = plain_document

    def test_marker_is_applied_retroactively(self) -> None:
        """Enabling the behavior marks content that already existed."""
        assert IFoundationMember.providedBy(self.document)

    def test_chain_gains_the_workflow(self) -> None:
        """So the adapter applies and the workflow joins the chain."""
        assert FOUNDATION_MEMBER_WORKFLOW in self.wftool.getChainFor(self.document)

    def test_state_falls_back_to_initial(self) -> None:
        """With no history for the workflow, the read falls back cleanly."""
        assert self.wftool.getInfoFor(self.document, WORKFLOW_STATES) == "pending"

    def test_transition_works_without_migration(self) -> None:
        """And the workflow is immediately usable."""
        api.content.transition(obj=self.document, transition="activate")

        assert self.wftool.getInfoFor(self.document, WORKFLOW_STATES) == "active"

    def test_review_state_is_untouched(self) -> None:
        """Publication is unaffected by the retroactive marking."""
        assert self.wftool.getInfoFor(self.document, "review_state") == "private"


@pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])
class TestContentCreatedAfterTheBehavior:
    """Behavior first, content second — the same outcome."""

    @pytest.fixture(autouse=True)
    def _setup(self, wftool: WorkflowTool, member_profile: Container) -> None:
        self.wftool = wftool
        self.profile = member_profile

    def test_marker_is_applied(self) -> None:
        """New content provides the behavior's marker."""
        assert IFoundationMember.providedBy(self.profile)

    def test_chain_gains_the_workflow(self) -> None:
        """And participates in the additional workflow."""
        assert FOUNDATION_MEMBER_WORKFLOW in self.wftool.getChainFor(self.profile)
