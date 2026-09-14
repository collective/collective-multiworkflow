"""What enabling a behavior does, and does not do, to content that already exists.

``test_profile_order`` shows that existing content joins the chain at once and
reads the contributed workflow's initial state. Two things that ``notifyCreated``
or a transition would have done have still not happened, and only an explicit
step makes them happen:

- the ``workflow_states`` catalog index still holds the chain the object was
  indexed with;
- the contributed workflow's permission map has never been applied to the
  object.
"""

from . import FOUNDATION_MEMBER_BEHAVIOR
from collective.multiworkflow import api as mw_api
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.demo.behavior import MEMBERSHIP_PERMISSION
from collective.multiworkflow.utils.workflow import format_state
from plone import api
from plone.dexterity.content import Container
from tests import flush_indexing
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
from tests import roles_for
from typing import Any

import pytest


#: The catalog value of the contributed workflow's initial state.
PENDING = format_state(FOUNDATION_MEMBER_WORKFLOW, "pending")

#: The roles the demo workflow's initial state maps its permission to.
PENDING_ROLES = ("Manager", "Reviewer", "Site Administrator")


@pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])
class TestBehaviorEnabledOnExistingContent:
    @pytest.fixture(autouse=True)
    def _setup(self, wftool: Any, catalog: Any, plain_document: Container) -> None:
        """Enable the behavior on Document after the Document already exists.

        The creation reindex is drained first. Left in the queue, it would run
        after the behavior is enabled, index the new chain, and hide exactly the
        staleness under test.
        """
        flush_indexing()
        fti = api.portal.get_tool("portal_types")[PLAIN_DOCUMENT["type"]]
        fti.manage_changeProperties(
            behaviors=[*fti.behaviors, FOUNDATION_MEMBER_BEHAVIOR]
        )
        self.wftool = wftool
        self.catalog = catalog
        self.document = plain_document
        self.path = "/".join(plain_document.getPhysicalPath())

    def _indexed_as_pending(self) -> bool:
        flush_indexing()
        return self.path in [
            brain.getPath() for brain in self.catalog(workflow_states=PENDING)
        ]

    def test_state_is_readable_at_once(self) -> None:
        """Reads fall back to the contributed workflow's initial state."""
        assert mw_api.get_states(self.document) == {
            PUBLICATION_WORKFLOW: "private",
            FOUNDATION_MEMBER_WORKFLOW: "pending",
        }

    def test_index_is_stale(self) -> None:
        """Nothing reindexes the object when the behavior is enabled."""
        assert not self._indexed_as_pending()

    def test_reindexing_the_index_repairs_it(self) -> None:
        """Reindexing ``workflow_states`` alone is enough."""
        self.catalog.reindexIndex("workflow_states", None)

        assert self._indexed_as_pending()

    def test_permission_map_is_not_applied(self) -> None:
        """The object still acquires the permission the workflow manages."""
        assert roles_for(self.document, MEMBERSHIP_PERMISSION) == ()

    def test_update_role_mappings_applies_it(self) -> None:
        """``updateRoleMappings`` applies the initial state's map."""
        self.wftool.updateRoleMappings()

        assert roles_for(self.document, MEMBERSHIP_PERMISSION) == PENDING_ROLES
