"""Tests for the ``workflow_states`` index, its ordering and its freshness.

Every assertion about the index goes through :meth:`_matches`, which flushes
CMFCore's indexing queue and then *queries*. Both halves matter. Without the
flush the catalog is an arbitrary number of operations behind, so the result
says more about queue draining than about the code under test. And querying
rather than reading the brain is the point of the exercise: ZCatalog rebuilds
metadata on a partial reindex, so a brain can carry the right value while the
index that should have found it is stale — an assertion on a brain would pass
either way.

Ordering is the one thing only the brain can show, since a KeywordIndex holds a
set. Those two tests read metadata, and say so.
"""

from . import AUDIT_WORKFLOW
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.utils.workflow import format_state
from collective.multiworkflow.utils.workflow import parse_state
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from plone import api
from plone.dexterity.content import Container
from tests import flush_indexing
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
from typing import Any

import pytest


class Searchable:
    """Query helpers shared by the classes that assert on the index."""

    catalog: Any
    document: Container

    def _matches(self, workflow_id: str, state: str) -> int:
        """Count the objects the index answers with for one chain entry.

        :param workflow_id: id of the workflow to look for.
        :param state: id of the state that workflow should be in.
        :returns: how many times *this* object matches — 0 or 1.
        """
        flush_indexing()
        return len(
            self.catalog(
                UID=self.document.UID(),
                **{WORKFLOW_STATES: format_state(workflow_id, state)},
            )
        )

    def _states(self) -> tuple[str, ...]:
        """Read the ordered chain off the object's brain.

        :returns: the metadata column, which is the only place order survives.
        """
        flush_indexing()
        brain = self.catalog(UID=self.document.UID())[0]
        return tuple(getattr(brain, WORKFLOW_STATES))


class TestIndexIsInstalled:
    @pytest.fixture(autouse=True)
    def _setup(self, catalog: Any) -> None:
        self.catalog = catalog

    def test_index_exists(self) -> None:
        """The add-on's own profile installs it."""
        assert WORKFLOW_STATES in self.catalog.indexes()

    def test_index_is_a_keyword_index(self) -> None:
        """One object holds several states, so it cannot be a FieldIndex."""
        assert self.catalog.Indexes[WORKFLOW_STATES].meta_type == "KeywordIndex"

    def test_metadata_column_exists(self) -> None:
        """Listings read the whole chain off the brain, without waking it."""
        assert WORKFLOW_STATES in self.catalog.schema()


class TestValueFormat:
    def test_round_trips(self) -> None:
        """Formatting and parsing are inverse."""
        assert parse_state(format_state("wf", "state")) == ("wf", "state")

    def test_a_bare_state_is_rejected(self) -> None:
        """A value without a workflow id is not a value of this index."""
        with pytest.raises(ValueError):
            parse_state("published")


@pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])
class TestNonParticipatingContent(Searchable):
    """Content nothing contributed to is described too, in a single entry."""

    @pytest.fixture(autouse=True)
    def _setup(self, catalog: Any, plain_document: Container) -> None:
        self.catalog = catalog
        self.document = plain_document

    def test_the_only_entry_is_the_configured_workflow(self) -> None:
        """So entry zero is readable without asking whether it participates."""
        assert self._states() == (format_state(PUBLICATION_WORKFLOW, "private"),)

    def test_it_is_findable_by_its_publication_state(self) -> None:
        """The index covers the whole site, not participating content alone."""
        assert self._matches(PUBLICATION_WORKFLOW, "private") == 1

    def test_publishing_moves_the_index(self) -> None:
        """``review_state`` is a chain variable CMFCore already reindexes, but
        the index named after it is not, so the entry needs following too."""
        api.content.transition(obj=self.document, transition="publish")

        assert self._matches(PUBLICATION_WORKFLOW, "published") == 1
        assert self._matches(PUBLICATION_WORKFLOW, "private") == 0


@pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])
class TestChainOrder(Searchable):
    """The type's own workflow first, contributions after, as declared."""

    @pytest.fixture(autouse=True)
    def _setup(self, catalog: Any, member_profile: Container) -> None:
        self.catalog = catalog
        self.document = member_profile

    def test_entries_are_in_chain_order(self) -> None:
        """Metadata preserves order; the index, being a set, cannot."""
        assert self._states() == (
            format_state(PUBLICATION_WORKFLOW, "private"),
            format_state(FOUNDATION_MEMBER_WORKFLOW, "pending"),
        )

    def test_the_first_entry_is_the_review_state(self) -> None:
        """The guarantee callers actually depend on, stated on its own."""
        workflow_id, state = parse_state(self._states()[0])

        assert workflow_id == PUBLICATION_WORKFLOW
        assert state == api.content.get_state(obj=self.document)


@pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])
class TestSharedStateVariableStaysFresh(Searchable):
    """A workflow adopting the indexed name is reindexed by CMFCore itself.

    ``WorkflowTool._reindexWorkflowVariables`` reindexes every index named
    after one of the chain's workflow variables, so the demo workflow — whose
    ``state_var`` *is* ``workflow_states`` — needs no help from the subscriber.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, catalog: Any, member_profile: Container) -> None:
        self.catalog = catalog
        self.document = member_profile

    def test_the_index_follows_a_secondary_transition(self) -> None:
        """The query moves, not merely the brain."""
        api.content.transition(obj=self.document, transition="activate")

        assert self._matches(FOUNDATION_MEMBER_WORKFLOW, "active") == 1
        assert self._matches(FOUNDATION_MEMBER_WORKFLOW, "pending") == 0

    def test_the_publication_entry_is_untouched(self) -> None:
        """Reindexing on one chain member must not disturb the others."""
        api.content.transition(obj=self.document, transition="activate")

        assert self._matches(PUBLICATION_WORKFLOW, "private") == 1


@pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])
class TestBespokeStateVariableStaysFresh(Searchable):
    """A workflow keeping its own state variable relies on the subscriber.

    Nothing in CMFCore reindexes ``workflow_states`` for such a chain, so
    without :func:`~collective.multiworkflow.subscribers.reindex.reindex_workflow_states`
    the index freezes at the values it held when the workflow was contributed —
    while the brain keeps reporting the truth. These are the assertions that
    catch that, and removing the subscriber turns every one of them red.
    """

    @pytest.fixture(autouse=True)
    def _setup(self, catalog: Any, audited_document: Container) -> None:
        self.catalog = catalog
        self.document = audited_document

    def test_the_contributed_workflow_is_indexed(self) -> None:
        """Reindexing after the contribution picks the new chain member up."""
        assert self._matches(AUDIT_WORKFLOW, "unaudited") == 1

    def test_the_index_follows_a_transition(self) -> None:
        """The subscriber's whole reason to exist."""
        api.content.transition(obj=self.document, transition="audit")

        assert self._matches(AUDIT_WORKFLOW, "audited") == 1
        assert self._matches(AUDIT_WORKFLOW, "unaudited") == 0

    def test_a_publication_transition_keeps_both_entries_right(self) -> None:
        """Driving one workflow leaves the other's entry alone."""
        api.content.transition(obj=self.document, transition="audit")
        api.content.transition(obj=self.document, transition="publish")

        assert self._matches(PUBLICATION_WORKFLOW, "published") == 1
        assert self._matches(AUDIT_WORKFLOW, "audited") == 1
