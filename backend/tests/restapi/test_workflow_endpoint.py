"""Functional tests for the ``@workflow`` endpoint.

Covers the contract the Volto add-on consumes: the additive ``chain`` key, the
top-level ``transitions`` list narrowed to the primary workflow, and — most
importantly — that content without additional workflows is served exactly the
payload core produces.
"""

from collections.abc import Iterator
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.interfaces import IAdditionalWorkflowLabel
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
from typing import Any
from zope.component import getGlobalSiteManager
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.simpletranslationdomain import SimpleTranslationDomain
from zope.i18nmessageid import MessageFactory

import pytest


pytestmark = pytest.mark.portal(
    content=[MEMBER_PROFILE, PLAIN_DOCUMENT],
    roles=["Manager"],
)


#: A translation domain of the tests' own, so a label's translation is observable.
LABEL_DOMAIN = "collective.multiworkflow.tests"

LABEL = "Foundation membership"

#: What ``LABEL_DOMAIN`` translates ``LABEL`` to in English.
TRANSLATED_LABEL = "Membership of the foundation"


@pytest.fixture()
def declared_label() -> Iterator[str]:
    """Label the demo's membership workflow, as the directive's ``label`` does.

    The label is a message id in a domain registered here, which translates it
    for English. A payload carrying the translation therefore proves the label
    was translated rather than passed on as it came.
    """
    gsm = getGlobalSiteManager()
    label = MessageFactory(LABEL_DOMAIN)(LABEL)
    domain = SimpleTranslationDomain(LABEL_DOMAIN, {("en", LABEL): TRANSLATED_LABEL})
    gsm.registerUtility(label, IAdditionalWorkflowLabel, FOUNDATION_MEMBER_WORKFLOW)
    gsm.registerUtility(domain, ITranslationDomain, LABEL_DOMAIN)

    yield label

    gsm.unregisterUtility(label, IAdditionalWorkflowLabel, FOUNDATION_MEMBER_WORKFLOW)
    gsm.unregisterUtility(domain, ITranslationDomain, LABEL_DOMAIN)


class TestDeclaredLabel:
    @pytest.fixture(autouse=True)
    def _setup(self, declared_label: str, member_payload: dict) -> None:
        self.chain = member_payload["chain"]

    def test_the_label_arrives_as_the_title_translated(self) -> None:
        """Clients show ``title``, so that is where the declared label goes."""
        assert self.chain[1]["title"] == TRANSLATED_LABEL

    def test_an_unlabelled_workflow_keeps_its_title(self) -> None:
        """The label names the membership workflow only."""
        assert self.chain[0]["title"] == "Simple Publication Workflow"


class TestChainKey:
    @pytest.fixture(autouse=True)
    def _setup(self, member_payload: dict) -> None:
        self.payload = member_payload
        self.secondary = member_payload["chain"][1]

    def test_chain_is_present(self) -> None:
        """Participating content gains the per-workflow breakdown."""
        assert "chain" in self.payload

    def test_chain_lists_both_workflows_in_order(self) -> None:
        """The configured chain leads; contributions follow."""
        ids = [entry["workflow_id"] for entry in self.payload["chain"]]

        assert ids == [PUBLICATION_WORKFLOW, FOUNDATION_MEMBER_WORKFLOW]

    def test_entry_reports_its_state_variable(self) -> None:
        """Each entry names the variable it drives."""
        variables = {
            entry["workflow_id"]: entry["state_variable"]
            for entry in self.payload["chain"]
        }

        assert variables == {
            PUBLICATION_WORKFLOW: "review_state",
            FOUNDATION_MEMBER_WORKFLOW: WORKFLOW_STATES,
        }

    def test_entry_reports_state_id_and_title(self) -> None:
        """States carry a title usable as a label."""
        assert self.secondary["state"] == {"id": "pending", "title": "Pending"}

    def test_entry_reports_workflow_title(self) -> None:
        """Each entry carries the workflow's own title."""
        assert self.secondary["title"] == "Membership"

    def test_secondary_transitions_are_grouped_under_their_workflow(self) -> None:
        """The membership transition appears in its own entry."""
        titles = [transition["title"] for transition in self.secondary["transitions"]]

        assert titles == ["Activate"]

    def test_transition_ids_are_actionable_urls(self) -> None:
        """Each transition's ``@id`` is the URL to POST to."""
        assert self.secondary["transitions"][0]["@id"].endswith("/@workflow/activate")

    def test_primary_entry_carries_publication_history(self) -> None:
        """The publication workflow reports its history."""
        assert [
            entry["review_state"] for entry in self.payload["chain"][0]["history"]
        ] == ["private"]

    def test_secondary_entry_carries_its_own_history(self) -> None:
        """Each entry reports the history of its own workflow, not the chain's."""
        assert [entry[WORKFLOW_STATES] for entry in self.secondary["history"]] == [
            "pending"
        ]


class TestTopLevelKeys:
    @pytest.fixture(autouse=True)
    def _setup(self, member_payload: dict) -> None:
        self.payload = member_payload

    def test_state_is_still_review_state(self) -> None:
        """The top-level state keeps reporting publication only."""
        assert self.payload["state"]["id"] == "private"

    def test_transitions_are_narrowed_to_the_primary_workflow(self) -> None:
        """Secondary transitions must not leak into the flat list."""
        titles = {transition["title"] for transition in self.payload["transitions"]}

        assert "Activate" not in titles
        assert "Publish" in titles

    def test_history_is_publication_history(self) -> None:
        """The top-level history is unchanged."""
        assert [entry["review_state"] for entry in self.payload["history"]] == [
            "private"
        ]


class TestNonParticipatingContentIsUntouched:
    @pytest.fixture(autouse=True)
    def _setup(self, plain_payload: dict) -> None:
        self.payload = plain_payload

    def test_no_chain_key(self) -> None:
        """Vanilla content gets exactly the stock payload."""
        assert "chain" not in self.payload

    def test_keys_match_core(self) -> None:
        """The key set is the one plone.restapi ships."""
        assert set(self.payload) == {"@id", "history", "transitions", "state"}

    def test_transitions_are_untouched(self) -> None:
        """Publication transitions are served as usual."""
        titles = {transition["title"] for transition in self.payload["transitions"]}

        assert "Publish" in titles


class TestTransitionsStillExecute:
    """Assertions go through HTTP so no transaction juggling is needed."""

    @pytest.fixture(autouse=True)
    def _setup(self, committed_portal: Any, manager_request: Any) -> None:
        self.request = manager_request

    def activate(self) -> Any:
        """Perform the membership transition.

        :returns: the raw POST response, for the one test that inspects it.
        """
        return self.request.post(f"/{MEMBER_PROFILE['id']}/@workflow/activate")

    def payload_after_activation(self) -> dict:
        """Transition, then re-read the endpoint.

        :returns: the ``@workflow`` payload after the transition.
        """
        self.activate()
        return self.request.get(f"/{MEMBER_PROFILE['id']}/@workflow").json()

    def test_post_secondary_transition(self) -> None:
        """A secondary transition is executable through the endpoint."""
        response = self.activate()

        assert response.status_code == 200, response.text

    def test_chain_reflects_the_new_state(self) -> None:
        """The payload follows the transition."""
        secondary = self.payload_after_activation()["chain"][1]

        assert secondary["state"]["id"] == "active"
        assert secondary["state_variable"] == WORKFLOW_STATES

    def test_secondary_transition_leaves_review_state_alone(self) -> None:
        """Publication is unaffected by a membership transition."""
        payload = self.payload_after_activation()

        assert payload["state"]["id"] == "private"
