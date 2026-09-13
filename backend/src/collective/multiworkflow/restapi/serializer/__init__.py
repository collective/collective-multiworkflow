"""Serializers for content with additional workflows.

Importing this subpackage applies the content serializer patch in
:mod:`collective.multiworkflow.restapi.serializer.dxcontent`. Including its
ZCML imports it.

BBB: in 1.0.0a1 this was a module holding
:class:`~collective.multiworkflow.restapi.serializer.workflow.WorkflowChainInfo`,
which is re-exported here so code importing it from this location keeps
working.
"""

from .dxcontent import apply_patch
from .workflow import WorkflowChainInfo


__all__ = ["WorkflowChainInfo"]


apply_patch()
