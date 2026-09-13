"""Tests for how permissions compose across a workflow chain.

Shared values for the package live here so test modules and ``conftest`` import
them relatively.

The claim under test: workflows sharing a chain each rewrite only the
permissions they declare, so **disjoint** sets compose and an **overlapping**
one is left as whichever workflow transitioned last wrote it.
"""

from collective.multiworkflow.interfaces import IAdditionalWorkflows
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES


MEMBERSHIP_WORKFLOW = "membership_workflow"
MEMBERSHIP_STATE_VAR = WORKFLOW_STATES

CLASHING_WORKFLOW = "clashing_workflow"
CLASHING_STATE_VAR = "clashing_state"

#: Declared by the package's ``permissions.zcml``; no core workflow claims it.
MEMBERSHIP_PERMISSION = "collective.multiworkflow: Manage membership"

#: One of the three the publication workflow manages, so a secondary workflow
#: declaring it produces the conflict this package is about.
SHARED_PERMISSION = "Modify portal content"


class IMember(IAdditionalWorkflows):
    """Marker contributing a workflow with a permission set of its own."""


class IClashing(IAdditionalWorkflows):
    """Marker contributing a workflow that claims a publication permission."""
