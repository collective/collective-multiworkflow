"""Patches to ``plone.exportimport``, kept together for upstreaming.

`plone.exportimport` restores an object's workflow state by assigning
``obj.workflow_history`` directly. That fires no transition, so none of the
machinery that keeps workflow variables catalogued ever runs:
``WorkflowTool._reindexWorkflowVariables`` is only reached through
``_invokeWithNotification``.

``review_state`` escapes the problem because ``update_review_state`` performs a
real transition just before. Any *other* workflow variable does not, and its
index keeps whatever value the object was first catalogued with — which is
exactly the state an additional workflow is in.

Measured on this package's own example content, importing an object whose
membership workflow is ``active``::

    object   foundation_member_workflow: active
    catalog  foundation_member_workflow|pending      <- stale

The publication state is right either way, so the staleness reads as a correct
index rather than a broken one.

The fix belongs upstream, in ``update_workflow_history``. Until it lands there,
this module applies it as a wrapper, in one place, shaped so that the body of
:func:`reindex_workflow_variables` can be moved into `plone.exportimport`
unchanged.

The patch is applied when this subpackage's ZCML is loaded, which the root
``configure.zcml`` does.
"""

from .. import logger
from functools import wraps
from plone import api
from plone.dexterity.content import DexterityContent
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.WorkflowTool import WorkflowTool
from typing import Any


#: Set once the patch is in place, so a second ZCML load cannot wrap the
#: wrapper.
_applied = False


def reindex_workflow_variables(obj: DexterityContent) -> DexterityContent:
    """Reindex the catalog indexes named after the object's workflow variables.

    This is the body proposed for `plone.exportimport`: it names no index of
    this package's own, and it is a no-op on a site whose content runs a single
    workflow, because ``review_state`` is already fresh by the time it runs.

    Only variables the catalog actually has an index for are reindexed. A
    workflow declaring a state variable no index is named after is therefore
    left alone here, as it is everywhere else in Plone.

    :param obj: the object whose workflow history was just restored.
    :returns: the same object, for chaining.
    """
    # The tools are typed as their interfaces rather than the implementations.
    wftool: WorkflowTool = api.portal.get_tool("portal_workflow")  # type: ignore[assignment]
    catalog: CatalogTool = api.portal.get_tool("portal_catalog")  # type: ignore[assignment]

    variables = wftool.getCatalogVariablesFor(obj) or {}
    idxs = [name for name in variables if name in catalog.indexes()]
    if idxs:
        obj.reindexObject(idxs=idxs)
    return obj


def apply_patches() -> None:
    """Wrap ``update_workflow_history`` so it reindexes what it changed.

    ``updaters()`` builds its list by reading the module globals each time it
    is called, so rebinding the module attribute is enough — no import in
    `plone.exportimport` holds an earlier reference to the original.

    Does nothing when `plone.exportimport` is absent. It is not a dependency of
    this package, nor of ``Products.CMFPlone``; it arrives with
    ``plone.distribution`` in a standard Plone installation.
    """
    global _applied
    if _applied:
        return

    try:
        from plone.exportimport.utils.content import import_helpers
    except ImportError:
        logger.debug(
            "plone.exportimport is not installed; workflow variables will not "
            "be reindexed on import."
        )
        return

    original = import_helpers.update_workflow_history

    # wraps() carries the docstring the importer logs as the updater's
    # description, and sets __wrapped__ — which is what lets the spike reach
    # the unpatched function and assert that upstream still needs this.
    @wraps(original)
    def update_workflow_history(item: dict, obj: Any) -> Any:
        """Restore the workflow history, then reindex what it changed.

        The reindex is conditional on the item actually carrying a history:
        the updater runs for every imported object, and most of them have
        nothing here to reindex for.
        """
        obj = original(item, obj)
        if item.get("workflow_history"):
            reindex_workflow_variables(obj)
        return obj

    #: Lets a test assert the patch is in place without comparing function
    #: identity against a closure.
    update_workflow_history.patched_by = __name__  # type: ignore[attr-defined]

    import_helpers.update_workflow_history = update_workflow_history
    _applied = True
    logger.debug("Patched plone.exportimport.update_workflow_history.")


apply_patches()
