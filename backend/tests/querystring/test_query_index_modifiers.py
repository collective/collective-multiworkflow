from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.indexers import format_state
from collective.multiworkflow.indexers import WORKFLOW_STATES
from collective.multiworkflow.querystring import query_index_modifiers
from tests import PUBLICATION_WORKFLOW
from typing import Any

import pytest


#: What a bare state id is read as: the site's default workflow, which is also
#: the workflow the index always lists first.
DEFAULT = PUBLICATION_WORKFLOW


@pytest.mark.portal()
class TestReviewStateModifier:
    @pytest.fixture(autouse=True)
    def _setup(self, portal: Any) -> None:
        self.modifier = query_index_modifiers.ReviewStateModifier()

    @pytest.mark.parametrize(
        "value,expected",
        [
            # A bare id is attributed to the default workflow, so a collection
            # written against review_state before this add-on keeps working.
            ({"query": "private"}, {"query": [format_state(DEFAULT, "private")]}),
            (
                {"query": ["private", "published"]},
                {
                    "query": [
                        format_state(DEFAULT, "private"),
                        format_state(DEFAULT, "published"),
                    ]
                },
            ),
            # An already-qualified value is left exactly as it is.
            (
                {"query": format_state(FOUNDATION_MEMBER_WORKFLOW, "pending")},
                {"query": [format_state(FOUNDATION_MEMBER_WORKFLOW, "pending")]},
            ),
            # Mixed input: only the bare half is touched.
            (
                {
                    "query": [
                        "private",
                        format_state(FOUNDATION_MEMBER_WORKFLOW, "pending"),
                    ]
                },
                {
                    "query": [
                        format_state(DEFAULT, "private"),
                        format_state(FOUNDATION_MEMBER_WORKFLOW, "pending"),
                    ]
                },
            ),
        ],
    )
    def test_query_values_are_qualified(self, value: dict, expected: dict) -> None:
        """A bare state id names no workflow, so the index cannot match it."""
        assert self.modifier(value) == (WORKFLOW_STATES, expected)

    def test_the_index_is_renamed(self) -> None:
        """Which is the modifier's reason to exist."""
        index, _ = self.modifier({"query": "private"})

        assert index == WORKFLOW_STATES

    def test_the_operator_survives(self) -> None:
        """*all of* parses to an ``and`` operator, and a KeywordIndex defaults
        to ``or`` — dropping it would silently widen the query."""
        _, query = self.modifier({"query": ["private"], "operator": "and"})

        assert query["operator"] == "and"

    def test_an_exclusion_survives(self) -> None:
        """*excludes* parses to a ``not`` key and carries no ``query`` at all."""
        _, query = self.modifier({"not": "private"})

        assert query == {"not": [format_state(DEFAULT, "private")]}

    def test_unknown_keys_are_passed_through(self) -> None:
        """The modifier renames an index; it does not curate the query."""
        _, query = self.modifier({"query": "private", "range": "min"})

        assert query["range"] == "min"

    def test_the_source_query_is_not_mutated(self) -> None:
        """The parser owns the dict it handed over."""
        value = {"query": "private"}

        self.modifier(value)

        assert value == {"query": "private"}
