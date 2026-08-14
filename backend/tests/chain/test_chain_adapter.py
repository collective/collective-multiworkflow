"""Tests for the workflow chain adapter.

Covers the invariants the mechanism must hold: the configured chain is only
appended to, composition is deterministic and deduplicated, a bad declaration
degrades gracefully, and content that does not participate is untouched.
"""

from . import IMember
from . import INotParticipating
from . import IPeerReviewed
from . import MEMBERSHIP_STATE_VAR
from . import MEMBERSHIP_WORKFLOW
from . import REVIEW_WORKFLOW
from collective.multiworkflow.chain import additional_workflows_chain
from plone.base.interfaces import IWorkflowChain
from plone.dexterity.content import Container
from Products.CMFPlone.WorkflowTool import WorkflowTool
from tests import BASE_CHAIN
from tests import PLAIN_DOCUMENT
from typing import Any
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import pytest


pytestmark = pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])


class TestChainComposition:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        member_document: Container,
        plain_document: Container,
        membership_workflow: Any,
        review_workflow: Any,
        register_contribution: Any,
    ) -> None:
        self.wftool = wftool
        self.member_document = member_document
        self.plain_document = plain_document
        self.contribute = register_contribution

    def test_configured_chain_is_appended_to(self) -> None:
        """I1: the type's configured chain is preserved and comes first."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)

        assert self.wftool.getChainFor(self.member_document) == (
            *BASE_CHAIN,
            MEMBERSHIP_WORKFLOW,
        )

    def test_multiple_markers_all_contribute(self) -> None:
        """An object providing two markers collects both contributions."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)
        self.contribute(IPeerReviewed, REVIEW_WORKFLOW)
        alsoProvides(self.plain_document, IMember)
        alsoProvides(self.plain_document, IPeerReviewed)

        chain = self.wftool.getChainFor(self.plain_document)

        assert set(chain) == {*BASE_CHAIN, MEMBERSHIP_WORKFLOW, REVIEW_WORKFLOW}
        assert chain[: len(BASE_CHAIN)] == BASE_CHAIN

    def test_one_marker_contributing_two_workflows(self) -> None:
        """A single marker may contribute more than one workflow, in order."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW, REVIEW_WORKFLOW)

        assert self.wftool.getChainFor(self.member_document) == (
            *BASE_CHAIN,
            MEMBERSHIP_WORKFLOW,
            REVIEW_WORKFLOW,
        )

    def test_composition_is_deduplicated(self) -> None:
        """I2: a workflow contributed twice appears once."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW, MEMBERSHIP_WORKFLOW)

        assert self.wftool.getChainFor(self.member_document) == (
            *BASE_CHAIN,
            MEMBERSHIP_WORKFLOW,
        )

    def test_contributing_the_base_workflow_is_a_noop(self) -> None:
        """I2: contributing a workflow already in the base chain adds nothing."""
        self.contribute(IMember, *BASE_CHAIN)

        assert self.wftool.getChainFor(self.member_document) == BASE_CHAIN

    def test_composition_is_stable_across_calls(self) -> None:
        """I2: repeated lookups return an identical chain."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW, REVIEW_WORKFLOW)

        first = self.wftool.getChainFor(self.member_document)
        second = self.wftool.getChainFor(self.member_document)

        assert first == second

    def test_lookup_does_not_recurse(self) -> None:
        """Reading the base chain must not re-enter the adapter."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)

        try:
            chain = self.wftool.getChainFor(self.member_document)
        except RecursionError:  # pragma: no cover - the failure being guarded
            pytest.fail("Reading the base chain re-entered the chain adapter")

        assert MEMBERSHIP_WORKFLOW in chain


class TestGracefulDegradation:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        member_document: Container,
        membership_workflow: Any,
        register_contribution: Any,
    ) -> None:
        self.wftool = wftool
        self.member_document = member_document
        self.contribute = register_contribution

    def test_unknown_workflow_is_skipped(self) -> None:
        """I3: an id absent from portal_workflow never breaks chain lookup."""
        self.contribute(IMember, "no_such_workflow")

        assert self.wftool.getChainFor(self.member_document) == BASE_CHAIN

    def test_unknown_workflow_is_logged(self, caplog: pytest.LogCaptureFixture) -> None:
        """I3: the skipped contribution is reported, not silently dropped."""
        self.contribute(IMember, "no_such_workflow")

        with caplog.at_level("WARNING", logger="collective.multiworkflow"):
            self.wftool.getChainFor(self.member_document)

        assert "no_such_workflow" in caplog.text

    def test_valid_contributions_survive_an_invalid_one(self) -> None:
        """A bad id does not discard the good ids declared alongside it."""
        self.contribute(IMember, "no_such_workflow", MEMBERSHIP_WORKFLOW)

        assert self.wftool.getChainFor(self.member_document) == (
            *BASE_CHAIN,
            MEMBERSHIP_WORKFLOW,
        )


class TestNonParticipatingContent:
    """``member_document`` is not bound here, and cannot be.

    That fixture applies ``IMember`` to ``plain_document`` *in place* — the two
    names are one object — so binding both in ``_setup`` would leave the
    supposedly plain Document marked, and the first two tests below would assert
    nothing. The tests that do want it marked take it as a parameter.
    """

    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        plain_document: Container,
        membership_workflow: Any,
        register_contribution: Any,
    ) -> None:
        self.wftool = wftool
        self.plain_document = plain_document
        self.contribute = register_contribution

    def test_plain_content_keeps_its_chain(self) -> None:
        """Content without a participating marker is untouched."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)

        assert self.wftool.getChainFor(self.plain_document) == BASE_CHAIN

    def test_unrelated_marker_does_not_participate(self) -> None:
        """A marker not extending the base marker contributes nothing."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)
        alsoProvides(self.plain_document, INotParticipating)

        assert self.wftool.getChainFor(self.plain_document) == BASE_CHAIN

    def test_marker_without_contribution_is_harmless(
        self, member_document: Container
    ) -> None:
        """A participating marker with no subscriber registered adds nothing."""
        assert self.wftool.getChainFor(member_document) == BASE_CHAIN

    def test_review_state_is_unaffected(self, member_document: Container) -> None:
        """The publication workflow keeps driving ``review_state``."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)
        self.wftool.notifyCreated(member_document)

        assert self.wftool.getInfoFor(member_document, "review_state") == "private"
        assert (
            self.wftool.getInfoFor(member_document, MEMBERSHIP_STATE_VAR) == "pending"
        )


class TestAdapterDirectly:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: WorkflowTool,
        member_document: Container,
        membership_workflow: Any,
        register_contribution: Any,
    ) -> None:
        self.wftool = wftool
        self.member_document = member_document
        self.contribute = register_contribution

    def test_adapter_is_registered_for_the_marker(self) -> None:
        """The ZCML registration is what makes ``getChainFor`` use our adapter."""
        chain = getMultiAdapter((self.member_document, self.wftool), IWorkflowChain)

        assert chain == BASE_CHAIN

    def test_adapter_returns_a_tuple(self) -> None:
        """The chain must be a tuple, as the rest of CMF expects."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)

        chain = additional_workflows_chain(self.member_document, self.wftool)

        assert isinstance(chain, tuple)
