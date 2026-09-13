"""The order in which several markers' contributions are appended.

Measured rather than designed. The chain adapter appends what
``collect_contributions`` returns, and ``zope.component.subscribers`` finds
subscribers by walking the object's interface resolution order from its least
specific end. The order is therefore decided by the order in which the object
provides the markers, not by the order in which the contributions were
registered:

- for behaviors, it is the reverse of the order they are listed in the type's
  ``behaviors``, so the behavior listed last contributes first;
- for markers applied with ``alsoProvides``, it is the reverse of the order
  they are given in.

Within one declaration, the ids keep the order they were declared in; see
``test_declaration``.
"""

from . import IMember
from . import IPeerReviewed
from . import MEMBERSHIP_WORKFLOW
from . import REVIEW_WORKFLOW
from collections.abc import Iterator
from plone import api
from plone.behavior.interfaces import IBehavior
from plone.behavior.registration import BehaviorRegistration
from plone.dexterity.content import Container
from tests import BASE_CHAIN
from tests import PLAIN_DOCUMENT
from typing import Any
from zope.component import getGlobalSiteManager
from zope.interface import alsoProvides

import pytest


#: ``(behavior name, marker, contributed workflow)`` for each participant.
MEMBER = ("tests.chain.member", IMember, MEMBERSHIP_WORKFLOW)
PEER_REVIEWED = ("tests.chain.peer_reviewed", IPeerReviewed, REVIEW_WORKFLOW)

ORDERINGS = [
    pytest.param((MEMBER, PEER_REVIEWED), id="member-first"),
    pytest.param((PEER_REVIEWED, MEMBER), id="peer-reviewed-first"),
]


def contributed(declarations: tuple[tuple[str, Any, str], ...]) -> tuple[str, ...]:
    """The workflow ids of some declarations, in the order given."""
    return tuple(workflow_id for _, _, workflow_id in declarations)


@pytest.fixture()
def register_behaviors() -> Iterator[Any]:
    """Register behaviors providing the given markers, and unregister them after."""
    # The global registry is typed as the lookup interface, which does not
    # declare the registration methods it implements.
    gsm: Any = getGlobalSiteManager()
    registered: list[tuple[BehaviorRegistration, str]] = []

    def _register(*declarations: tuple[str, Any, str]) -> None:
        for name, marker, _ in declarations:
            registration = BehaviorRegistration(
                title=name,
                description="",
                interface=marker,
                marker=marker,
                factory=None,
                name=name,
            )
            gsm.registerUtility(registration, IBehavior, name=name)
            registered.append((registration, name))

    yield _register

    for registration, name in registered:
        gsm.unregisterUtility(registration, IBehavior, name=name)


@pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])
class TestBehaviorsOnAType:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: Any,
        plain_document: Container,
        membership_workflow: Any,
        review_workflow: Any,
        register_contribution: Any,
        register_behaviors: Any,
    ) -> None:
        self.wftool = wftool
        self.document = plain_document
        self.contribute = register_contribution
        self.register_behaviors = register_behaviors

    def enable(self, declarations: tuple[tuple[str, Any, str], ...]) -> None:
        fti = api.portal.get_tool("portal_types")[PLAIN_DOCUMENT["type"]]
        fti.manage_changeProperties(
            behaviors=[*fti.behaviors, *[name for name, _, _ in declarations]]
        )

    @pytest.mark.parametrize("registration", ORDERINGS)
    @pytest.mark.parametrize("listing", ORDERINGS)
    def test_last_listed_behavior_contributes_first(
        self,
        registration: tuple[tuple[str, Any, str], ...],
        listing: tuple[tuple[str, Any, str], ...],
    ) -> None:
        """Whatever the registration order, the listing order decides."""
        for _, marker, workflow_id in registration:
            self.contribute(marker, workflow_id)
        self.register_behaviors(*registration)

        self.enable(listing)

        assert self.wftool.getChainFor(self.document) == (
            *BASE_CHAIN,
            *reversed(contributed(listing)),
        )


@pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])
class TestDirectlyProvidedMarkers:
    @pytest.fixture(autouse=True)
    def _setup(
        self,
        wftool: Any,
        plain_document: Container,
        membership_workflow: Any,
        review_workflow: Any,
        register_contribution: Any,
    ) -> None:
        self.wftool = wftool
        self.document = plain_document
        self.contribute = register_contribution

    @pytest.mark.parametrize("registration", ORDERINGS)
    @pytest.mark.parametrize("provision", ORDERINGS)
    def test_last_provided_marker_contributes_first(
        self,
        registration: tuple[tuple[str, Any, str], ...],
        provision: tuple[tuple[str, Any, str], ...],
    ) -> None:
        """Whatever the registration order, the ``alsoProvides`` order decides."""
        for _, marker, workflow_id in registration:
            self.contribute(marker, workflow_id)

        alsoProvides(self.document, *[marker for _, marker, _ in provision])

        assert self.wftool.getChainFor(self.document) == (
            *BASE_CHAIN,
            *reversed(contributed(provision)),
        )
