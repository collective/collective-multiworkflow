---
myst:
  html_meta:
    "description": "Symptoms you may meet with additional workflows, what causes each one, how to check for it, and how to fix it."
    "property=og:description": "Symptoms you may meet with additional workflows, what causes each one, how to check for it, and how to fix it."
    "property=og:title": "How to troubleshoot additional workflows"
    "keywords": "Plone, collective.multiworkflow, troubleshooting, chain, catalog, permissions, Volto"
---

(howto-troubleshoot)=

# How to troubleshoot additional workflows

This guide lists the symptoms you are most likely to meet, with the cause of each, a check that confirms it, and the fix.

In the snippets, `obj` is a content object showing the symptom.
Run them wherever you can reach your site from Python, such as a debug session or a test.

(troubleshoot-chain)=

## The chain has only the publication workflow

Your workflow is missing from `portal_workflow.getChainFor(obj)`, the `@workflow` endpoint has no `chain` for the object, and Volto shows the publication workflow alone.

Check the object in this order.

```python
from collective.multiworkflow.declaration import collect_contributions
from collective.multiworkflow.interfaces import IAdditionalWorkflows

assert IAdditionalWorkflows.providedBy(obj)
assert collect_contributions(obj) == ("foundation_member_workflow",)
```

If the first assertion fails, the object provides no participating marker.

- The behavior is not enabled on the object's type. Enable it, as in {doc}`declare-additional-workflows`.
- The behavior is registered with a `factory` and no `marker`. `plone.behavior` then never applies the interface to the object. Give the behavior a `marker`.
- The marker does not extend `IAdditionalWorkflows`. The ZCML directive refuses such a marker at start-up, so this happens only when the contribution is registered from Python. Make the marker extend `IAdditionalWorkflows`.

If the second assertion fails, nothing declares a contribution for the marker.
The ZCML holding the `<plone:additionalworkflows />` directive is not loaded, or the instance has not been restarted since you added it.

If both pass, the contributed id names no workflow in `portal_workflow`.
The chain adapter skips such an id rather than break chain lookup, and logs a warning each time it resolves the object's chain.

```text
Workflow 'membership_workflow' contributed to '/plone/member-profile' does not exist in portal_workflow; skipping it.
```

Correct the id in the directive, or install the workflow by applying the profile that holds its definition.

(troubleshoot-transition)=

## A transition moves the wrong workflow

Executing a transition changes the state of a workflow other than the one you meant, and the state of yours stays where it was.

Two workflows in the chain define a transition with the same id.
Without a workflow named, `portal_workflow.doActionFor` executes the transition in the first workflow, in chain order, that can execute it from its current state.
`plone.api.content.transition` and `mw_api.transition` without `workflow_id` go through `doActionFor`, so which workflow moves can change as the object's states change.

List the workflows defining the id.

```python
from plone import api

wftool = api.portal.get_tool("portal_workflow")
transition_id = "publish"

claimants = [
    workflow.getId()
    for workflow in wftool.getWorkflowsFor(obj)
    if transition_id in workflow.transitions.objectIds()
]
```

More than one id in `claimants` confirms the collision.

To execute the transition now, name its workflow.

```python
from collective.multiworkflow import api as mw_api

mw_api.transition(obj, "publish", workflow_id="listing_workflow")
```

To fix it for good, give the transitions of your workflow ids no other workflow uses, as {doc}`write-a-composing-workflow` describes.

(troubleshoot-access)=

## Access changes after a transition in another workflow

A user gains or loses access to an object after a transition in a workflow that should not affect it, and the access changes back after a transition in the other workflow.

Two workflows in the chain manage the same permission, and the mapping of that permission is whatever the workflow that transitioned last wrote.
{doc}`/concepts/permissions` explains why.

```python
from collective.multiworkflow import api as mw_api

assert mw_api.conflicting_permissions(obj) == {}
```

A mapping that is not empty names each shared permission and the workflows claiming it, in chain order.
Remove the permission from all but one of them, as {doc}`audit-permission-conflicts` describes.

(troubleshoot-search)=

## A search by an additional state finds nothing

A catalog query on `workflow_states`, or a collection criterion naming an additional state, returns no results although matching content exists.

Check that the index exists and holds objects.

```python
from plone import api

catalog = api.portal.get_tool("portal_catalog")

assert "workflow_states" in catalog.indexes()
assert catalog.Indexes["workflow_states"].numObjects() > 0
```

If the first assertion fails, the add-on's profile is not installed in the site.
Install it, as in {doc}`install`.

If the second fails on a site with content, the content was created before the add-on was installed and has never been indexed under the new index.
Reindex it, as in {doc}`add-to-an-existing-site`.

If both pass, check the value you query for.
The index holds qualified values only, so a bare state id matches nothing.

```python
from collective.multiworkflow.utils.workflow import format_state

assert len(catalog(workflow_states="pending")) == 0

value = format_state("foundation_member_workflow", "pending")
assert len(catalog(workflow_states=value)) > 0
```

Build the value with `format_state`, as {doc}`search-by-workflow-state` shows.

If most content is found and only content older than the behavior is missing, see {ref}`troubleshoot-existing-content`.

(troubleshoot-frontend)=

## Volto shows only the publication workflow

The workflow control in the Volto toolbar has a single selector, for the publication workflow, although the content has an additional workflow.

Check the backend first.
Request the content's `@workflow` endpoint, as in {doc}`consume-the-rest-api`.
If the response has no `chain` key, or a `chain` holding the publication workflow alone, the backend contributes nothing to the object, and the add-on correctly renders nothing more: see {ref}`troubleshoot-chain`.

If the `chain` holds your workflow, the frontend is not using the add-on.

- The package is installed but not listed in `addons`. An add-on missing from `addons` contributes nothing, and its shadows of Volto's components are never resolved. Register it, as in {doc}`install`, then restart or rebuild the frontend.
- Another add-on, or your project, shadows Volto's `Workflow` component too, and its shadow applies instead. See {doc}`customize-the-volto-components` for which shadow wins and how to combine them.

(troubleshoot-existing-content)=

## Content that existed before the behavior is missing from searches

Content created after you enabled a participating behavior is found by its additional state, and content that already existed is not.
Its access is unchanged as well, even though the contributed workflow manages a permission.

Enabling a behavior makes existing content join the chain and read the contributed workflow's initial state, but it neither reindexes that content nor applies the workflow's permission map to it.
{doc}`/concepts/behavior-driven-assignment` explains why.

```python
from collective.multiworkflow import api as mw_api
from collective.multiworkflow.utils.workflow import format_state
from plone import api

workflow_id = "foundation_member_workflow"
state = mw_api.get_state(obj, workflow_id=workflow_id)

catalog = api.portal.get_tool("portal_catalog")
found = catalog(workflow_states=format_state(workflow_id, state), UID=obj.UID())
assert len(found) == 1
```

An empty result confirms it.
Reindex the index and update the role mappings, as in {doc}`declare-additional-workflows`, in the step that brings existing content up to date.

(troubleshoot-order)=

## The workflows are in an unexpected order

`portal_workflow.getChainFor(obj)` lists the contributed workflows in an order other than the one you expected, and so do the `@workflow` endpoint's `chain` and the Volto controls.

When several behaviors on a type contribute workflows, their workflows are appended in the reverse of the order the type lists the behaviors in: the behavior listed last contributes first.
The order in which the ZCML declares the contributions plays no part.

Change the order of the type's `behaviors` to change the order of the chain.
{ref}`reference-zcml-order` gives the rule in full, with an example.

```{seealso}
{doc}`/concepts/index` for why the package behaves the way it does, which often explains a surprise before it needs troubleshooting.
```
