"""Tests for the ``<plone:additionalworkflows />`` ZCML directive.

The demo package registers its contribution through this directive, so the rest
of the suite already covers the happy path end to end. What is pinned here is
the directive's own contract: the ids it registers, their order, the label it
may declare, and the configuration-time errors that stop a declaration which
could never work.
"""

from . import MEMBERSHIP_WORKFLOW
from . import REVIEW_WORKFLOW
from collections.abc import Callable
from collections.abc import Iterator
from collective.multiworkflow.declaration import collect_contributions
from collective.multiworkflow.declaration import workflow_label
from plone.dexterity.content import Container
from plone.testing import zca
from tests import PLAIN_DOCUMENT
from typing import Any
from zope.configuration import xmlconfig
from zope.configuration.config import ConfigurationConflictError
from zope.configuration.exceptions import ConfigurationError
from zope.i18nmessageid import Message

import collective.multiworkflow
import pytest


pytestmark = pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])

#: The i18n domain the snippets declare, and so the domain of any label.
DOMAIN = "collective.multiworkflow.tests"

#: The directive under test needs a namespace declaration to be usable.
SNIPPET = f"""\
<configure
    xmlns:plone="http://namespaces.plone.org/plone"
    i18n_domain="{DOMAIN}"
    >
  %s
</configure>
"""

LABEL = "Foundation membership"


@pytest.fixture()
def load_zcml() -> Iterator[Callable[[str], None]]:
    """Execute a ZCML snippet against a throwaway component registry.

    Registrations made by the snippet are discarded afterwards, so a test
    cannot leak a subscriber into the ones that follow.
    """
    zca.pushGlobalRegistry()
    # meta.zcml is what binds the directive to its handler; the test layer has
    # already loaded it, but this machine needs its own copy.
    context = xmlconfig.file("meta.zcml", collective.multiworkflow)

    def _load(directive: str) -> None:
        xmlconfig.string(SNIPPET % directive, context=context)

    yield _load

    zca.popGlobalRegistry()


class TestAdditionalWorkflowsDirective:
    @pytest.fixture(autouse=True)
    def _setup(self, member_document: Container, load_zcml: Any) -> None:
        self.document = member_document
        self.load_zcml = load_zcml

    def test_registers_the_contribution(self) -> None:
        """One line of ZCML is all a behavior needs."""
        self.load_zcml(
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{MEMBERSHIP_WORKFLOW}" />'
        )

        assert collect_contributions(self.document) == (MEMBERSHIP_WORKFLOW,)

    def test_several_workflows_keep_their_order(self) -> None:
        """``workflows`` is a whitespace-separated list, read left to right."""
        self.load_zcml(
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{REVIEW_WORKFLOW} {MEMBERSHIP_WORKFLOW}" />'
        )

        assert collect_contributions(self.document) == (
            REVIEW_WORKFLOW,
            MEMBERSHIP_WORKFLOW,
        )

    def test_a_label_does_not_change_the_contribution(self) -> None:
        """``label`` names the workflow; what is appended stays the same."""
        self.load_zcml(
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{MEMBERSHIP_WORKFLOW}" label="{LABEL}" />'
        )

        assert collect_contributions(self.document) == (MEMBERSHIP_WORKFLOW,)


class TestRegistrationIsPerMarker:
    """``member_document`` is deliberately not bound here.

    It applies ``IMember`` to ``plain_document`` in place — one object, two
    names — so binding it would leave nothing unmarked to compare against.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, plain_document: Container, load_zcml: Any) -> None:
        self.document = plain_document
        self.load_zcml = load_zcml

    def test_unmarked_content_is_unaffected(self) -> None:
        """The registration is per marker, exactly as the subscriber form was."""
        self.load_zcml(
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{MEMBERSHIP_WORKFLOW}" />'
        )

        assert collect_contributions(self.document) == ()


class TestLabel:
    @pytest.fixture(autouse=True)
    def _setup(
        self, membership_workflow: Any, review_workflow: Any, load_zcml: Any
    ) -> None:
        self.membership = membership_workflow
        self.review = review_workflow
        self.load_zcml = load_zcml

    def test_the_label_names_the_workflow(self) -> None:
        """A declared label replaces the workflow's title."""
        self.membership.title = "Membership"
        self.load_zcml(
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{MEMBERSHIP_WORKFLOW}" label="{LABEL}" />'
        )

        assert workflow_label(self.membership) == LABEL

    def test_the_label_is_translatable(self) -> None:
        """It is a message id in the domain of the ZCML file declaring it."""
        self.load_zcml(
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{MEMBERSHIP_WORKFLOW}" label="{LABEL}" />'
        )

        label = workflow_label(self.membership)

        assert isinstance(label, Message)
        assert label.domain == DOMAIN

    def test_without_a_label_the_title_is_used(self) -> None:
        """Declaring no label keeps the behavior from before labels existed."""
        self.membership.title = "Membership"
        self.load_zcml(
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{MEMBERSHIP_WORKFLOW}" />'
        )

        assert workflow_label(self.membership) == "Membership"

    def test_a_label_names_its_own_workflow_only(self) -> None:
        """Another workflow contributed by the same marker keeps its title."""
        self.review.title = "Peer review"
        self.load_zcml(
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{MEMBERSHIP_WORKFLOW}" label="{LABEL}" />'
            f'<plone:additionalworkflows marker="tests.chain.IMember" '
            f'workflows="{REVIEW_WORKFLOW}" />'
        )

        assert workflow_label(self.review) == "Peer review"


class TestMarkerIsValidatedAtConfigurationTime:
    """A marker that cannot work fails while the ZCML is read, not silently."""

    @pytest.fixture(autouse=True)
    def _setup(self, load_zcml: Any) -> None:
        self.load_zcml = load_zcml

    def test_marker_must_extend_the_base_marker(self) -> None:
        """The chain adapter is registered for ``IAdditionalWorkflows`` only."""
        with pytest.raises(ConfigurationError):
            self.load_zcml(
                "<plone:additionalworkflows "
                'marker="tests.chain.INotParticipating" '
                f'workflows="{MEMBERSHIP_WORKFLOW}" />'
            )

    def test_the_error_names_the_offending_marker(self) -> None:
        """So the fix is obvious from the traceback alone."""
        with pytest.raises(ConfigurationError) as raised:
            self.load_zcml(
                "<plone:additionalworkflows "
                'marker="tests.chain.INotParticipating" '
                f'workflows="{MEMBERSHIP_WORKFLOW}" />'
            )

        assert "INotParticipating" in str(raised.value)
        assert "IAdditionalWorkflows" in str(raised.value)

    def test_the_base_marker_itself_is_rejected(self) -> None:
        """``extends`` is strict: contributing to the base marker is a mistake."""
        with pytest.raises(ConfigurationError):
            self.load_zcml(
                "<plone:additionalworkflows "
                'marker="collective.multiworkflow.interfaces.IAdditionalWorkflows" '
                f'workflows="{MEMBERSHIP_WORKFLOW}" />'
            )


class TestLabelIsValidatedAtConfigurationTime:
    """A label that could name the wrong workflow fails while the ZCML is read."""

    @pytest.fixture(autouse=True)
    def _setup(self, load_zcml: Any) -> None:
        self.load_zcml = load_zcml

    def test_a_label_needs_exactly_one_workflow(self) -> None:
        """With several ids, nothing says which workflow the label names."""
        with pytest.raises(ConfigurationError) as raised:
            self.load_zcml(
                f'<plone:additionalworkflows marker="tests.chain.IMember" '
                f'workflows="{REVIEW_WORKFLOW} {MEMBERSHIP_WORKFLOW}" '
                f'label="{LABEL}" />'
            )

        assert REVIEW_WORKFLOW in str(raised.value)
        assert MEMBERSHIP_WORKFLOW in str(raised.value)

    def test_one_workflow_cannot_be_labelled_twice(self) -> None:
        """The label belongs to the workflow, so two labels for it conflict."""
        with pytest.raises(ConfigurationConflictError):
            self.load_zcml(
                f'<plone:additionalworkflows marker="tests.chain.IMember" '
                f'workflows="{MEMBERSHIP_WORKFLOW}" label="{LABEL}" />'
                f'<plone:additionalworkflows marker="tests.chain.IPeerReviewed" '
                f'workflows="{MEMBERSHIP_WORKFLOW}" label="Membership" />'
            )
