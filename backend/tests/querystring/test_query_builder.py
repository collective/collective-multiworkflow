from plone import api
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
            # stores it: read as belonging to the default workflow, so it
            # finds exactly what the qualified criterion above finds.
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
