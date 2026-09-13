---
myst:
  html_meta:
    "description": "What to check and change when moving a site or a project to a newer release of collective.multiworkflow."
    "property=og:description": "What to check and change when moving a site or a project to a newer release of collective.multiworkflow."
    "property=og:title": "How to upgrade to a newer release"
    "keywords": "Plone, collective.multiworkflow, upgrade, release, migration, Volto"
---

(howto-upgrade)=

# How to upgrade to a newer release

This guide shows you what to check and change when you move a site or a project to a newer release of `collective.multiworkflow` and `@plone-collective/volto-multiworkflow`.

Releases are listed newest first.
If you skip a release, work through every section between the release you run and the one you are moving to, oldest first.

## From 1.0.0a1 to 1.0.0a2

The backend package `1.0.0a2` and the Volto add-on `1.0.0-alpha.2` are released together.
Upgrade both.

| Change | Affects | Action |
|---|---|---|
| Backend modules reorganized | code or ZCML naming the add-on's modules | {ref}`upgrade-moved-imports` |
| `review_state` criteria with bare state ids stay on `review_state` | collections and listings using the **Review state** criterion | {ref}`upgrade-check-review-state-criteria` |
| Imported content gets the role mappings of its restored state | sites populated through `plone.exportimport` | {ref}`upgrade-repair-imported-content` |
| `workflow_states` in content serializations and summaries | REST API clients, and serializers of your own | {ref}`upgrade-expect-workflow-states` |
| `label` attribute on `<plone:additionalworkflows />` | packages contributing workflows | optional, {ref}`upgrade-label-workflows` |
| `@history` no longer depends on include order | projects working around a startup error | {ref}`upgrade-cmfeditions-workaround` |
| `workflow_states` helpers and `StateBadge` values | Volto projects | {ref}`upgrade-frontend-projects` |

### Prerequisites

- A site running `collective.multiworkflow` `1.0.0a1`.
- A backup of the database, as for any upgrade.

### 1. Update the packages

Pin the new releases in your project.

```toml
dependencies = [
    "collective.multiworkflow==1.0.0a2",
]
```

```json
"dependencies": {
  "@plone-collective/volto-multiworkflow": "1.0.0-alpha.2"
}
```

A specifier such as `>=1.0.0a1` or `^1.0.0-alpha.1` already admits the new release, so refreshing your lock file is enough.

Restart the backend, because the ZCML changed.

This release has no GenericSetup upgrade step.
The `collective.multiworkflow:default` profile is still version `1000`, and the catalog index, the metadata column, and the registry records it installs are unchanged, so there is nothing to run in {guilabel}`Add-ons`.

(upgrade-moved-imports)=

### 2. Update imports of moved modules

The backend is now organized by concern, and the names below moved.
Every one of them except the indexer is still importable from its `1.0.0a1` location, so existing code keeps working.
The old locations are kept for backward compatibility only, so update your imports all the same.

| Name | `1.0.0a1` location | New location | Old location still works |
|---|---|---|---|
| `format_state`, `parse_state`, `WORKFLOW_STATES`, `STATE_SEPARATOR` | `collective.multiworkflow.indexers` | `collective.multiworkflow.utils.workflow` | yes |
| `reindex_workflow_states` | `collective.multiworkflow.indexers` | `collective.multiworkflow.subscribers.reindex` | yes |
| `WorkflowChainInfo` | `collective.multiworkflow.restapi.serializer` | `collective.multiworkflow.restapi.serializer.workflow` | yes |
| `WorkflowChainInfoService` | `collective.multiworkflow.restapi.service` | `collective.multiworkflow.restapi.services.workflow.get` | yes |
| `ChainHistoryGet`, `ChainHistoryViewlet` | `collective.multiworkflow.restapi.history` | `collective.multiworkflow.restapi.services.history.get` | yes |
| `workflow_states` (the indexer) | `collective.multiworkflow.indexers` | `collective.multiworkflow.indexers.workflow_states` | no, see below |

The empty `collective.multiworkflow.serializers` package is gone.
Remove any `<include package="collective.multiworkflow.serializers" />`.

```{warning}
`from collective.multiworkflow.indexers import workflow_states` does not fail.
It now imports the `workflow_states` *module*, and the error surfaces only when that module is called: `TypeError: 'module' object is not callable`.
Import the function from `collective.multiworkflow.indexers.workflow_states` instead.
```

Search for every old location, in Python and in ZCML alike, such as an `overrides.zcml` registering a subclass of `WorkflowChainInfo`.

```shell
grep -rn -e "multiworkflow.indexers" -e "multiworkflow.restapi" -e "multiworkflow.serializers" src/ tests/
```

While you are there, replace any `<workflow-id>|<state-id>` string built or split by hand with `format_state` and `parse_state`.

The {doc}`/reference/api/index` lists every public name at its current location.

(upgrade-check-review-state-criteria)=

### 3. Check `review_state` criteria

Version `1.0.0a1` moved every parsed `review_state` query onto the `workflow_states` index, and qualified a bare state id, such as `published`, with the first workflow of the site's default chain.
Content whose `review_state` is driven by another workflow therefore dropped out of those results.

Version `1.0.0a2` moves a query only when one of its values names a workflow.

- A criterion whose values name no workflow stays on the stock `review_state` index, and matches every object in that state, whichever workflow drives it.
  This is how it behaved before the add-on was installed.
- A criterion whose values are all qualified, which is what the collection editor saves, moves to `workflow_states`, unchanged from `1.0.0a1`.
- A criterion mixing both still moves, and its bare ids are still qualified with the default workflow.

Bare values come from collections and listing blocks stored before the add-on was installed, and from queries built in code or sent to `@querystring-search`.
Check the result count of each one that matters.
If a result grows because it now includes types driven by other workflows, and the narrower result was what you wanted, qualify the value, as in `simple_publication_workflow|published`, or save the criterion again from the collection editor.

Direct catalog queries are not affected.
They were never rewritten.
Neither are query fields and index modifiers of your own that already target `workflow_states` with qualified values.

```{note}
A parsed query holds one entry per index, so two criteria that both end up on `workflow_states` cannot be combined: one replaces the other.
With `1.0.0a1` that included every **Review state** criterion, so it could not be combined with a query field of your own mapped onto `workflow_states`.
A **Review state** criterion with bare ids now stays on `review_state`, and combines with such a field.
A qualified one still does not.
```

(upgrade-repair-imported-content)=

### 4. Repair content imported with `1.0.0a1`

Skip this unless the site was populated through `plone.exportimport` while `1.0.0a1` was installed, including a `plone.distribution` site creation or a profile that imports example content.

`plone.exportimport` restores workflow state by writing `workflow_history` directly, which fires no transition.
Version `1.0.0a1` already repaired the catalog entries of such content, but not its role mappings: an object imported in an additional workflow's `active` state kept the permissions of that workflow's initial state.
Version `1.0.0a2` reapplies each workflow's permission map on import, so content imported from now on needs nothing.

Repair content imported earlier once, from a script or an upgrade step of your own.

```python
from plone import api

wftool = api.portal.get_tool("portal_workflow")
wftool.updateRoleMappings()
```

This is what the **Update security settings** button of `portal_workflow` does in the Zope Management Interface.
It is safe to run again.
{doc}`add-to-an-existing-site` explains how to check a single object.

If your project worked around the problem by calling `updateRoleMappings`, `updateRoleMappingsFor`, or `reindexObjectSecurity` after a `plone.exportimport` import, the workaround is now redundant.
It is harmless, and you can remove it, with one exception.

The importer reapplies the permission maps of the workflows in an object's chain *when its history is restored*.
A workflow contributed through a marker that your code applies with `alsoProvides` joins the chain only once that marker is set.
If the marker may be set after the history is restored, for example by a subscriber or by a later step of your import, keep a site-wide `updateRoleMappings()` after the import.

```{important}
The fix covers `plone.exportimport`'s content importer only.
Code that writes `workflow_history` itself, such as a script importing members from another system, fires no transition either, and still has to call `updateRoleMappingsFor` for each workflow it writes, then `reindexObjectSecurity`, and reindex `workflow_states`.
```

(upgrade-expect-workflow-states)=

### 5. Expect `workflow_states` in REST API responses

The serialization of every Dexterity object, and every summary of a catalog result, now carries a `workflow_states` list: the object's state in every workflow of its chain, formatted as the catalog index holds it.
Summaries include the listings of `@search`, `@querystring-search`, and a folder's `items`.

```json
"workflow_states": [
  "simple_publication_workflow|published",
  "membership_workflow|active"
]
```

The key is added beside the existing ones, and no existing key changes value.

- A client validating responses against a closed schema has to allow the new key.
- A client requesting the key through `metadata_fields=workflow_states` keeps working, and can drop the parameter.
- An `IJSONSummarySerializerMetadata` utility of your own naming `workflow_states` is now redundant, and harmless.
- A custom serializer overriding `__call__` without calling `super()` does not carry the key.

#### If a serializer of yours already sets `workflow_states`

Check your own serializers for a `workflow_states` key before you upgrade.
A serializer that calls `super().__call__()` and then writes a `workflow_states` key of its own, such as the dictionary that `collective.multiworkflow.api.get_states` returns, overwrites the add-on's list for its content type only.
Clients then receive a dictionary for that type and a list for every other one, and code expecting one shape fails on the other.

Choose one shape.

- **Adopt the list.**
  Remove your key, and read a workflow's state from the list.

  ```python
  from collective.multiworkflow.utils.workflow import parse_state

  states = dict(parse_state(value) for value in result["workflow_states"])
  ```

  In Volto, parse the values with `parseWorkflowState`, as shown in {ref}`upgrade-frontend-projects`.
- **Keep your dictionary under another key.**
  Rename it, and update the clients reading it.

In both cases update tests asserting the dictionary, and any TypeScript type declaring `workflow_states` as a record.

{doc}`/reference/rest-api` shows the payloads.

(upgrade-label-workflows)=

### 6. Name contributed workflows with a label

This step is optional.
Without a label, every workflow is shown under its own title, exactly as in `1.0.0a1`.

A `label` on the directive names the workflow wherever the user interface names it: the `title` of its `@workflow` chain entry, the Volto workflow control and history, and the options of the **Review state** criterion.

```xml
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:plone="http://namespaces.plone.org/plone"
    i18n_domain="my.package"
    >

  <plone:additionalworkflows
      marker=".behaviors.IMembership"
      workflows="membership_workflow"
      label="Membership"
      />

</configure>
```

- The label is translated in the `i18n_domain` of the ZCML file declaring it.
- A directive with a `label` must list exactly one workflow, or the configuration fails to load.
  Split a directive that contributes several workflows into one directive per labelled workflow.
- Two directives labelling the same workflow conflict while the configuration is read.

Restart the backend after adding a label.
{doc}`declare-additional-workflows` covers the directive in full.

(upgrade-cmfeditions-workaround)=

### 7. Remove the include-order workaround for `@history`

With `1.0.0a1`, startup failed with a `ComponentLookupError` for `CMFEditions.AccessPreviousVersions` when a package included `collective.multiworkflow` before `Products.CMFEditions` had been configured.
The add-on now loads that permission itself.

If your `dependencies.zcml` includes `Products.CMFEditions`, or its `permissions.zcml`, before `collective.multiworkflow` only to avoid that error, the include is no longer needed.
It is harmless to keep.

(upgrade-frontend-projects)=

### 8. Update Volto projects

Nothing in a Volto project has to change, unless it declares a `workflow_states` key of its own, as described in {ref}`upgrade-expect-workflow-states`.
The shadowed `Workflow` and `History` components are unchanged, so a project shadowing them on top of the add-on keeps its customizations as they are.
The add-on's own strings are now in its message catalogs, so they render translated.

The release adds the following.

- `StateBadge` renders from a `workflow_states` value, with an optional translated `label`, as well as from a chain entry.
  `<StateBadge entry={entry} />` keeps working.
- `getWorkflowStates`, `getAdditionalWorkflowStates`, `parseWorkflowState`, and `formatWorkflowState` read and build `workflow_states` values.
  Replace any local code splitting those values on `|` with them.
- `WORKFLOW_STATE_SEPARATOR` and `WORKFLOW_STATES_VOCABULARY` name the separator and the vocabulary holding each value's translated title.
- The `WorkflowStateValue`, `ParsedWorkflowState`, and `WithWorkflowStates` types describe those values.

Reading one workflow's state from content or a summary takes no further request.

```ts
import {
  getWorkflowStates,
  parseWorkflowState,
} from '@plone-collective/volto-multiworkflow';

const providerState = getWorkflowStates(content)
  .map(parseWorkflowState)
  .find((state) => state?.workflow_id === 'provider_workflow')?.state_id;
```

{doc}`customize-the-volto-components` shows how to render those states in a listing.

```{note}
In TypeScript, `StateBadgeProps` is now a union of `EntryStateBadgeProps` and `ValueStateBadgeProps`.
An interface extending `StateBadgeProps` no longer compiles; extend one of the two instead.
```

### 9. Verify

After restarting both the backend and the frontend, check the following.

- The site starts with no configuration error.
- `GET @workflow` on content with an additional workflow returns a `chain` key, with each entry's `title` being the label you declared, if any.
- The serialization of every content type, and each item of a `GET @search` response, carries `workflow_states` as a list.
- The collections and listings you checked in step 3 return what you expect.
- An object imported before the upgrade grants the permissions of the state it is in.

```{seealso}
The changelogs of [`collective.multiworkflow`](https://github.com/collective/collective-multiworkflow/blob/main/backend/CHANGELOG.md) and [`@plone-collective/volto-multiworkflow`](https://github.com/collective/collective-multiworkflow/blob/main/frontend/packages/volto-multiworkflow/CHANGELOG.md) for the complete list of changes.
```
