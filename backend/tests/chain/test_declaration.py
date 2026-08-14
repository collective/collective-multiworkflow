"""Tests for the contribution declaration API."""

from . import IMember
from . import IPeerReviewed
from . import MEMBERSHIP_WORKFLOW
from . import REVIEW_WORKFLOW
from collective.multiworkflow.declaration import collect_contributions
from collective.multiworkflow.declaration import contributes
from collective.multiworkflow.interfaces import IAdditionalWorkflowsFor
from plone.dexterity.content import Container
from tests import PLAIN_DOCUMENT
from typing import Any
from zope.interface import alsoProvides

import pytest


class TestContributes:
    """Pure unit tests: the factory needs no portal at all."""

    def test_factory_returns_declared_ids(self) -> None:
        """The built factory yields exactly the ids it was given."""
        factory = contributes(IMember, MEMBERSHIP_WORKFLOW, REVIEW_WORKFLOW)

        assert factory(object()) == (MEMBERSHIP_WORKFLOW, REVIEW_WORKFLOW)

    def test_factory_declares_the_provided_interface(self) -> None:
        """ZCA registration relies on the factory's own declaration."""
        factory = contributes(IMember, MEMBERSHIP_WORKFLOW)

        assert IAdditionalWorkflowsFor.implementedBy(factory)

    def test_declaring_no_workflows_is_allowed(self) -> None:
        """An empty declaration is valid and contributes nothing."""
        factory = contributes(IMember)

        assert factory(object()) == ()


@pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])
class TestCollectContributions:
    """``member_document`` stays a parameter, as in ``test_chain_adapter``.

    It marks ``plain_document`` in place, so binding both would leave the plain
    Document marked and make the first test below assert nothing.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, plain_document: Container, register_contribution: Any) -> None:
        self.plain_document = plain_document
        self.contribute = register_contribution

    def test_no_marker_collects_nothing(self) -> None:
        """Plain content contributes no workflows."""
        assert collect_contributions(self.plain_document) == ()

    def test_single_marker(self, member_document: Container) -> None:
        """One registered subscriber contributes its ids."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)

        assert collect_contributions(member_document) == (MEMBERSHIP_WORKFLOW,)

    def test_two_markers_are_both_collected(self) -> None:
        """Subscription adapters accumulate rather than override."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)
        self.contribute(IPeerReviewed, REVIEW_WORKFLOW)
        alsoProvides(self.plain_document, IMember)
        alsoProvides(self.plain_document, IPeerReviewed)

        assert set(collect_contributions(self.plain_document)) == {
            MEMBERSHIP_WORKFLOW,
            REVIEW_WORKFLOW,
        }

    def test_duplicates_across_markers_collapse(self) -> None:
        """The same id contributed by two markers appears once."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW)
        self.contribute(IPeerReviewed, MEMBERSHIP_WORKFLOW)
        alsoProvides(self.plain_document, IMember)
        alsoProvides(self.plain_document, IPeerReviewed)

        assert collect_contributions(self.plain_document) == (MEMBERSHIP_WORKFLOW,)

    def test_order_is_stable(self, member_document: Container) -> None:
        """Repeated collection returns the same order."""
        self.contribute(IMember, MEMBERSHIP_WORKFLOW, REVIEW_WORKFLOW)

        assert collect_contributions(member_document) == collect_contributions(
            member_document
        )

    def test_declaration_order_within_a_marker_is_preserved(
        self, member_document: Container
    ) -> None:
        """Ids keep the order the behavior declared them in."""
        self.contribute(IMember, REVIEW_WORKFLOW, MEMBERSHIP_WORKFLOW)

        assert collect_contributions(member_document) == (
            REVIEW_WORKFLOW,
            MEMBERSHIP_WORKFLOW,
        )

    @pytest.mark.parametrize("workflow_id", ["", " "])
    def test_blank_ids_are_passed_through(
        self, member_document: Container, workflow_id: str
    ) -> None:
        """Validation of ids is the chain adapter's job, not the collector's."""
        self.contribute(IMember, workflow_id)

        assert collect_contributions(member_document) == (workflow_id,)
