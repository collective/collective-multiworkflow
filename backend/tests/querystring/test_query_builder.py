from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from plone import api
from plone.app.querystring.queryparser import parseAndModifyFormquery
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT

import pytest


@pytest.mark.portal(content=[MEMBER_PROFILE, PLAIN_DOCUMENT], roles=["Manager"])
class TestQueryBuilder:
    @pytest.fixture(autouse=True)
    def _setup(self, portal, http_request):
        self.portal = portal
        self.view = api.content.get_view(
            "querybuildernumberofresults", self.portal, http_request
        )

    @pytest.mark.parametrize(
        "query,total_results",
        [
            (
                [
                    {
                        "i": "review_state",
                        "o": "plone.app.querystring.operation.string.is",
                        "v": "simple_publication_workflow|private",
                    }
                ],
                2,
            ),
            (
                [
                    {
                        "i": "review_state",
                        "o": "plone.app.querystring.operation.string.is",
                        "v": "foundation_member_workflow|pending",
                    }
                ],
                1,
            ),
            # A bare state id, as a collection written before this add-on
            # stores it: left on the stock review_state index, which finds
            # exactly what the qualified criterion above finds.
            (
                [
                    {
                        "i": "review_state",
                        "o": "plone.app.querystring.operation.string.is",
                        "v": "private",
                    }
                ],
                2,
            ),
        ],
    )
    def test_results(self, query, total_results):
        with api.env.adopt_roles(["Manager"]):
            results = self.view(query=query)
        assert results.actual_result_count == total_results

    @pytest.mark.parametrize(
        "value,index",
        [
            ("private", "review_state"),
            ("simple_publication_workflow|private", WORKFLOW_STATES),
        ],
    )
    def test_queried_index(self, value, index):
        """Only a criterion naming a workflow is moved onto the chain index."""
        query = [
            {
                "i": "review_state",
                "o": "plone.app.querystring.operation.string.is",
                "v": value,
            }
        ]

        parsed = parseAndModifyFormquery(self.portal, query)

        assert {"review_state", WORKFLOW_STATES} & set(parsed) == {index}
