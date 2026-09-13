"""BBB: the ``@workflow`` GET service moved.

It lives in :mod:`collective.multiworkflow.restapi.services.workflow.get`. This
module re-exports it, so code importing it from its 1.0.0a1 location keeps
working. Nothing registers the service from here.
"""

from .services.workflow.get import WorkflowChainInfoService


__all__ = ["WorkflowChainInfoService"]
