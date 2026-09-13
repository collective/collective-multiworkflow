"""Tests for the workflow chain mechanism.

Shared values for the package live here so test modules and ``conftest`` import
them relatively.
"""

from collective.multiworkflow.interfaces import IAdditionalWorkflows
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from zope.interface import Interface


MEMBERSHIP_WORKFLOW = "membership_workflow"

#: This one follows the recommendation and shares the indexed state variable.
MEMBERSHIP_STATE_VAR = WORKFLOW_STATES

REVIEW_WORKFLOW = "peer_review_workflow"

#: And this one keeps a bespoke variable, the way a workflow written before the
#: index existed does — so the chain exercises both halves of the freshness
#: contract at once.
REVIEW_STATE_VAR = "peer_review_state"


class IMember(IAdditionalWorkflows):
    """Example behavior marker contributing a membership workflow."""


class IPeerReviewed(IAdditionalWorkflows):
    """A second marker, so multi-marker collection can be exercised."""


class INotParticipating(Interface):
    """A marker that does not extend the participation base marker."""
