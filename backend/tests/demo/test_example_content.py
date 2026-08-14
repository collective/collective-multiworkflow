"""The example-content profile actually creates its content.

Functional, not integration, and deliberately so: the importer behind this
profile commits as it goes. A functional layer stacks a ``DemoStorage`` per
test and pops it afterwards, so those commits are discarded; an integration
layer relies on ``transaction.abort()``, which a commit defeats — which is
exactly why this profile is kept separate from ``demo``.
"""

from . import CONTENT_PROFILE
from . import EXAMPLE_DOCUMENT
from . import EXAMPLE_PROFILE_ITEM
from collective.multiworkflow.demo.behavior import IFoundationMember
from plone.app.testing import applyProfile
from plone.dexterity.content import Container
from Products.CMFPlone.Portal import PloneSite

import pytest


class TestExampleContentProfile:
    @pytest.fixture(autouse=True)
    def _setup(self, functional_portal: PloneSite) -> None:
        """The portal with the example-content profile applied."""
        applyProfile(functional_portal, CONTENT_PROFILE)
        self.portal = functional_portal
        self.document: Container = functional_portal[EXAMPLE_DOCUMENT]

    def test_document_is_created(self) -> None:
        """The example Document lands at the site root."""
        assert EXAMPLE_DOCUMENT in self.portal

    def test_profile_item_is_created(self) -> None:
        """So does the example item of the custom type."""
        assert EXAMPLE_PROFILE_ITEM in self.document

    def test_imported_profile_participates(self) -> None:
        """The imported item of the participating type carries the behavior.

        Its Document parent deliberately does not: the demo profile touches no
        type Plone already shipped.
        """
        profile_item = self.document[EXAMPLE_PROFILE_ITEM]

        assert IFoundationMember.providedBy(profile_item)
        assert not IFoundationMember.providedBy(self.document)
