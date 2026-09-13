"""Patches to ``plone.exportimport``, kept together for upstreaming.

`plone.exportimport` restores an object's workflow state by assigning
``obj.workflow_history`` directly. That fires no transition, and so skips both
things a transition does once the new status is recorded:
``DCWorkflowDefinition.updateRoleMappingsFor``, which applies the state's
permission map to the object, and ``WorkflowTool._reindexWorkflowVariables``,
which catalogs the workflow variables and the object's security.

``review_state`` escapes the problem because ``update_review_state`` performs a
real transition just before. No other workflow is transitioned, so the object
keeps the role mappings and the catalog entry of the state it was created in:
its workflow's initial state.

Measured on this package's own example content, importing an object whose
membership workflow is ``active``::

    object       foundation_member_workflow: active
    catalog      foundation_member_workflow|pending      <- stale
    permissions  as mapped for pending                   <- stale

The publication state is right either way, so the import reads as correct
rather than broken. On a site whose own subscribers recompute role mappings
when an object is modified, it can also look intermittent: creating a child
inside an imported container repairs that container, and nothing else.

The fix belongs upstream, in ``update_workflow_history``. Until it lands there,
this module applies it as a wrapper, in one place, shaped so that the bodies of
:func:`update_role_mappings` and :func:`reindex_workflow_variables` can be moved
into `plone.exportimport` unchanged.

The patch is applied when this subpackage's ZCML is loaded, which the root
``configure.zcml`` does.
"""

from .. import logger
from Acquisition import aq_base
from functools import wraps
from plone import api
from plone.dexterity.content import DexterityContent
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.WorkflowTool import WorkflowTool
from typing import Any


#: Set once the patch is in place, so a second ZCML load cannot wrap the
#: wrapper.
_applied = False


def update_role_mappings(obj: DexterityContent) -> DexterityContent:
    """Apply the permission map of the state each workflow was restored to.

    Every workflow in the object's chain recomputes the mappings it manages
    from the object's current status, and the object's security is reindexed
    when any of them changed, as it would be after a transition.

    ``WorkflowTool`` has no per-object ``updateRoleMappingsFor``, only the
    site-wide ``updateRoleMappings``, which walks the whole portal. Iterating
    the object's own chain is the targeted equivalent. On a site whose content
    runs a single workflow it changes nothing, because ``update_review_state``
    has already transitioned that workflow.

    :param obj: the object whose workflow history was just restored.
    :returns: the same object, for chaining.
    """
    # The tool is typed as its interface rather than the implementation.
    wftool: WorkflowTool = api.portal.get_tool("portal_workflow")  # type: ignore[assignment]

    changed = False
    for workflow in wftool.getWorkflowsFor(obj):
        # aq_base: the method must belong to the workflow itself, not be
        # acquired from the tool or the portal above it.
        if hasattr(aq_base(workflow), "updateRoleMappingsFor"):
            changed = bool(workflow.updateRoleMappingsFor(obj)) or changed
    if changed:
        obj.reindexObjectSecurity()
    return obj


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
    """Wrap ``update_workflow_history`` so it finishes what a transition would.

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
            "plone.exportimport is not installed; imported content will keep "
            "the role mappings and index entries of its initial state."
        )
        return

    original = import_helpers.update_workflow_history

    # wraps() carries the docstring the importer logs as the updater's
    # description, and sets __wrapped__ — which is what lets the spike reach
    # the unpatched function and assert that upstream still needs this.
    @wraps(original)
    def update_workflow_history(item: dict, obj: Any) -> Any:
        """Restore the workflow history, then do what a transition would have.

        The follow-up is conditional on the item actually carrying a history:
        the updater runs for every imported object, and most of them have
        nothing here to act on. Role mappings come first, mirroring the order
        of a transition.
        """
        obj = original(item, obj)
        if item.get("workflow_history"):
            update_role_mappings(obj)
            reindex_workflow_variables(obj)
        return obj

    #: Lets a test assert the patch is in place without comparing function
    #: identity against a closure.
    update_workflow_history.patched_by = __name__  # type: ignore[attr-defined]

    import_helpers.update_workflow_history = update_workflow_history
    _applied = True
    logger.debug("Patched plone.exportimport.update_workflow_history.")


apply_patches()
