"""Tests for the ``<plone:additionalworkflows />`` ZCML directive.

The demo package registers its contribution through this directive, so the rest
of the suite already covers the happy path end to end. What is pinned here is
the directive's own contract: the ids it registers, their order, and the
configuration-time error that stops a marker which could never work.
"""

from . import MEMBERSHIP_WORKFLOW
from . import REVIEW_WORKFLOW
from collections.abc import Callable
from collections.abc import Iterator
from collective.multiworkflow.declaration import collect_contributions
from plone.dexterity.content import Container
from plone.testing import zca
from tests import PLAIN_DOCUMENT
from typing import Any
from zope.configuration import xmlconfig
from zope.configuration.exceptions import ConfigurationError

import collective.multiworkflow
import pytest


pytestmark = pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])

#: The directive under test needs a namespace declaration to be usable.
SNIPPET = """\
<configure xmlns:plone="http://namespaces.plone.org/plone">
  %s
</configure>
"""


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
