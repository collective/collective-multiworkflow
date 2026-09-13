"""BBB: the ``@history`` GET service and its viewlet moved.

They live in :mod:`collective.multiworkflow.restapi.services.history.get`. This
module re-exports them, so code importing them from their 1.0.0a1 location
keeps working. Nothing registers the service from here.
"""

from .services.history.get import ChainHistoryGet
from .services.history.get import ChainHistoryViewlet


__all__ = ["ChainHistoryGet", "ChainHistoryViewlet"]
