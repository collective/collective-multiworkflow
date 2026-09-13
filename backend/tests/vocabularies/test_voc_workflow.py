from collections.abc import Iterator
from collective.multiworkflow.demo.behavior import FOUNDATION_MEMBER_WORKFLOW
from collective.multiworkflow.interfaces import IAdditionalWorkflowLabel
from plone.app.vocabularies import SimpleTerm
from plone.app.vocabularies import SimpleVocabulary
from zope.component import getGlobalSiteManager

import pytest


class TestVocab:
    name: str = "collective.multiworkflow.vocabularies.WorkflowStates"
    vocab_type = SimpleVocabulary

    @pytest.fixture(autouse=True)
    def _setup(self, portal_class, get_vocabulary):
        self.portal = portal_class
        self.vocab = get_vocabulary(self.name, self.portal)

    def test_vocabulary_type(self):
        assert isinstance(self.vocab, self.vocab_type)

    @pytest.mark.parametrize(
        "token,title",
        [
            (
                "foundation_member_workflow|pending",
                "Membership: Pending",
            ),
            (
                "foundation_member_workflow|lapsed",
                "Membership: Lapsed",
            ),
            ("foundation_member_workflow|active", "Membership: Active"),
            (
                "simple_publication_workflow|private",
                "Simple Publication Workflow: Private",
            ),
            (
                "simple_publication_workflow|published",
                "Simple Publication Workflow: Published",
            ),
        ],
    )
    def test_vocab_terms(self, token: str, title: str):
        term = self.vocab.getTermByToken(token)
        assert isinstance(term, SimpleTerm)
        assert term.title == title
        assert term.token == token


class TestVocabWithDeclaredLabel:
    name: str = "collective.multiworkflow.vocabularies.WorkflowStates"

    @pytest.fixture()
    def declared_label(self) -> Iterator[str]:
        """Label the demo's membership workflow, as the directive's ``label`` does."""
        gsm = getGlobalSiteManager()
        label = "Foundation membership"
        gsm.registerUtility(label, IAdditionalWorkflowLabel, FOUNDATION_MEMBER_WORKFLOW)
        yield label
        gsm.unregisterUtility(
            label, IAdditionalWorkflowLabel, FOUNDATION_MEMBER_WORKFLOW
        )

    @pytest.fixture(autouse=True)
    def _setup(self, declared_label, portal_class, get_vocabulary):
        self.vocab = get_vocabulary(self.name, portal_class)

    def test_the_label_names_the_workflow(self):
        """The collection editor shows the same name as the ``@workflow`` payload."""
        term = self.vocab.getTermByToken("foundation_member_workflow|pending")
        assert term.title == "Foundation membership: Pending"

    def test_an_unlabelled_workflow_keeps_its_title(self):
        term = self.vocab.getTermByToken("simple_publication_workflow|private")
        assert term.title == "Simple Publication Workflow: Private"
