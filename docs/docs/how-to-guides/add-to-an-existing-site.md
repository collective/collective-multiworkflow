---
myst:
  html_meta:
    "description": "Add the package to a site that already has content, and reindex so the new index is populated."
    "property=og:description": "Add the package to a site that already has content, and reindex so the new index is populated."
    "property=og:title": "How to add the package to an existing site"
    "keywords": "Plone, collective.multiworkflow, upgrade, reindex, catalog, migration"
---

(howto-add-to-an-existing-site)=

# How to add the package to an existing site

This guide shows you what to do after installing the add-on on a site that already holds content.

Installing changes no content and no chain.
The one thing that needs attention is the catalog: a new index starts empty.

## Prerequisites

- The add-on installed, as described in {doc}`install`.
- A maintenance window proportional to the size of the site, for step 1.

## 1. Populate the new index

Reindex the site under the new index alone.

```python
from plone import api

catalog = api.portal.get_tool("portal_catalog")
catalog.reindexIndex("workflow_states", None)
```

From an upgrade step, do the same thing, and let it commit as your upgrade profile normally does.

```{note}
Reindexing one index is much cheaper than `clearFindAndRebuild()`, and it is all this add-on needs.
Reach for a full rebuild only if something else in the same upgrade calls for one.
```

Verify afterwards.

```python
assert catalog.Indexes["workflow_states"].numObjects() > 0
```

Every object now carries at least one value: its publication workflow's state.
Objects gain further values as behaviors contribute workflows to them.

## 2. Repair content imported before this version

Skip this unless the site was populated with `plone.exportimport`, or with a tool built on it such as a `plone.distribution` site creation.

Importing content restores workflow state by writing it directly rather than by transitioning.
That used to leave the chain index holding the state each object was created in, and the object's permissions set as that initial state defines them.
This package now patches the importer, so content imported from here on is indexed and secured correctly and needs nothing.

Content imported *before* you installed this version needs two repairs.
The reindex in step 1, which you have already run, repairs the index.
Recomputing role mappings repairs the permissions.

```python
wftool = api.portal.get_tool("portal_workflow")
wftool.updateRoleMappings()
```

`updateRoleMappings` walks the whole site, applies each workflow's permission map for the state every object is in, and reindexes the security of the objects whose mappings changed.
It is what the **Update security settings** button of `portal_workflow` does in the Zope Management Interface.
If you are unsure whether an import predates the patch, both repairs are safe to run again.

To check a single object rather than trust the answer, compare what it says with what the catalog says.

```python
from collective.multiworkflow import api as mw_api
from collective.multiworkflow.utils.workflow import format_state

states = mw_api.get_states(obj)
brain = api.content.find(UID=obj.UID())[0]

assert set(brain.workflow_states) == {
    format_state(workflow_id, state_id)
    for workflow_id, state_id in states.items()
}
```

A mismatch means the index is stale for that object, and only a reindex fixes it.

## 3. Check existing collections

Stored collections need no edit.
A `review_state` criterion whose values name no workflow is left on the stock `review_state` index, which still holds what it held before the add-on was installed.

Spot-check the ones that matter most, all the same—a collection whose result count changes has something else going on, and you want to know before your editors do.

## 4. Expect nothing else to change

The following are unaffected, and are worth verifying if you want reassurance rather than trust.

- **Chains.** No content type's configured chain is edited, so `getChainFor` answers exactly as before for every object until a behavior contributes to it.
- **`review_state`.** Unchanged in the catalog, in the API, and in the user interface.
- **REST API payloads.** `@workflow` gains a `chain` key on participating content only, and `@history` gains a `workflow_id` key on every entry.
  No existing key changes value.
- **Volto.** The shadowed components render as upstream on content with no additional workflows.

## 5. Then add a behavior

Nothing about the site changes until you declare one.
Continue with {doc}`declare-additional-workflows`.

```{seealso}
{doc}`/reference/catalog` for what the index holds, and {doc}`/reference/rest-api` for the exact payload additions.
```
