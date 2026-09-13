from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.querystring import query_index_modifiers
from collective.multiworkflow.querystring.query_index_modifiers import REVIEW_STATE
from collective.multiworkflow.utils.workflow import format_state
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from tests import PUBLICATION_WORKFLOW
from typing import Any

import pytest


#: What a bare state id is read as once its query has to move: the site's default
#: workflow, which is also the workflow the index always lists first.
DEFAULT = PUBLICATION_WORKFLOW

#: A qualified value of a workflow other than the default one.
PENDING_MEMBER = format_state(FOUNDATION_MEMBER_WORKFLOW, "pending")


@pytest.mark.portal()
class TestReviewStateModifier:
    @pytest.fixture(autouse=True)
    def _setup(self, portal: Any) -> None:
        self.modifier = query_index_modifiers.ReviewStateModifier()

    @pytest.mark.parametrize(
        "value",
        [
            {"query": "private"},
            {"query": ["private", "published"]},
            {"query": ["private"], "operator": "and"},
            {"not": "private"},
            # Nothing names a workflow, so nothing justifies moving the query.
            {"query": []},
        ],
    )
    def test_bare_queries_stay_on_review_state(self, value: dict) -> None:
        """A collection written before this add-on keeps its index and its query."""
        assert self.modifier(value) == (REVIEW_STATE, value)

    @pytest.mark.parametrize(
        "value,expected",
        [
            ({"query": PENDING_MEMBER}, {"query": [PENDING_MEMBER]}),
            (
                {"query": [format_state(DEFAULT, "private"), PENDING_MEMBER]},
                {"query": [format_state(DEFAULT, "private"), PENDING_MEMBER]},
            ),
            ({"not": PENDING_MEMBER}, {"not": [PENDING_MEMBER]}),
        ],
    )
    def test_qualified_queries_move_to_workflow_states(
        self, value: dict, expected: dict
    ) -> None:
        """A value naming its workflow can only be matched by the chain index."""
        assert self.modifier(value) == (WORKFLOW_STATES, expected)

    @pytest.mark.parametrize(
        "value,expected",
        [
            (
                {"query": ["private", PENDING_MEMBER]},
                {"query": [format_state(DEFAULT, "private"), PENDING_MEMBER]},
            ),
            (
                {"not": ["private", PENDING_MEMBER]},
                {"not": [format_state(DEFAULT, "private"), PENDING_MEMBER]},
            ),
        ],
    )
    def test_mixed_queries_qualify_the_bare_values(
        self, value: dict, expected: dict
    ) -> None:
        """Splitting one criterion across two indexes would AND what it ORs."""
        assert self.modifier(value) == (WORKFLOW_STATES, expected)

    def test_the_operator_survives_the_move(self) -> None:
        """*all of* parses to an ``and`` operator, and a KeywordIndex defaults
        to ``or`` — dropping it would silently widen the query."""
        _, query = self.modifier({"query": [PENDING_MEMBER], "operator": "and"})

        assert query["operator"] == "and"

    def test_unknown_keys_are_passed_through(self) -> None:
        """The modifier chooses an index; it does not curate the query."""
        _, query = self.modifier({"query": PENDING_MEMBER, "range": "min"})

        assert query["range"] == "min"

    @pytest.mark.parametrize("state", ["private", PENDING_MEMBER])
    def test_the_source_query_is_not_mutated(self, state: str) -> None:
        """The parser owns the dict it handed over."""
        value = {"query": state}

        self.modifier(value)

        assert value == {"query": state}
