"""Add ``workflow_states`` to `plone.restapi`'s content serialization.

The key sits beside ``review_state`` in the payload of every Dexterity object,
carrying the object's state in every workflow of its chain, formatted as the
``workflow_states`` catalog index holds it.

The patch wraps ``SerializeToJson.__call__`` on the class itself, rather than
binding a subclass in its place. ``SerializeFolderToJson``,
``SerializeCollectionToJson`` and any serializer an add-on derives from them
reach it through ``super().__call__``, so they all carry the key. And because
`plone.restapi`'s ZCML registers the very class that was patched, the order in
which the two packages are configured does not matter.

A subclass overriding ``__call__`` without calling ``super()`` does not carry
the key. Nothing short of patching that subclass as well could change that.

The patch is applied when :mod:`collective.multiworkflow.restapi.serializer` is
imported, which including its ZCML does.
"""

from collective.multiworkflow import logger
from collective.multiworkflow.utils.workflow import formatted_workflow_states
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from functools import wraps
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxcontent import SerializeToJson


#: Set once the patch is in place, so a second import cannot wrap the wrapper.
_applied = False


def apply_patch() -> None:
    """Wrap ``SerializeToJson.__call__`` so its payload carries ``workflow_states``.

    The original method stays reachable as ``__wrapped__``, which is what lets
    the spike test assert that upstream still lacks the key.
    """
    global _applied
    if _applied:
        return

    original = SerializeToJson.__call__

    @wraps(original)
    def __call__(
        self: SerializeToJson,
        version: str | None = None,
        include_items: bool = True,
        include_expansion: bool = True,
    ) -> dict:
        """Serialize the object, adding its state in every workflow of its chain.

        The states are read from the same object ``review_state`` is read from:
        the context itself, or the historical version being serialized.
        """
        result = original(
            self,
            version=version,
            include_items=include_items,
            include_expansion=include_expansion,
        )
        obj = self.context if version in (None, "current") else self.getVersion(version)
        result[WORKFLOW_STATES] = json_compatible(formatted_workflow_states(obj))
        return result

    #: Lets a test assert the patch is in place without comparing function
    #: identity against a closure.
    __call__.patched_by = __name__  # type: ignore[attr-defined]

    # method-assign: replacing the method on the class itself is the point of
    # the patch; every subclass resolves ``__call__`` through it.
    SerializeToJson.__call__ = __call__  # type: ignore[method-assign]
    _applied = True
    logger.debug("Patched plone.restapi.serializer.dxcontent.SerializeToJson.")
