---
myst:
  html_meta:
    "description": "Every public name in collective.multiworkflow, grouped by module."
    "property=og:description": "Every public name in collective.multiworkflow, grouped by module."
    "property=og:title": "Python API"
    "keywords": "Plone, collective.multiworkflow, API, Python, reference"
---

```{eval-rst}
.. currentmodule:: collective.multiworkflow
```

(reference-api)=

# Python API

The pages below are generated from the source.
They are the authoritative description of every public name this package offers.

```{toctree}
:maxdepth: 1
:hidden: true

api
declaration
interfaces
chain
utils
indexers
subscribers
querystring
vocabularies
restapi
exportimport
```

## `collective.multiworkflow.api`

Workflow-aware equivalents of the `plone.api` workflow helpers.
Called without a `workflow_id`, each behaves exactly as its `plone.api` counterpart.

```{eval-rst}
.. autosummary::

    api.get_state
    api.get_states
    api.transition
    api.transitions
    api.conflicting_permissions
    api.owning_workflow
```

## `collective.multiworkflow.declaration`

Registration of the workflows a behavior contributes.
Most callers use {ref}`the ZCML directive <reference-zcml>` instead of these.

```{eval-rst}
.. autosummary::

    declaration.contributes
    declaration.collect_contributions
    declaration.workflow_label
```

## `collective.multiworkflow.interfaces`

The interfaces the mechanism is built on.

```{eval-rst}
.. autosummary::

    interfaces.IAdditionalWorkflows
    interfaces.IAdditionalWorkflowsFor
    interfaces.IAdditionalWorkflowLabel
```

## `collective.multiworkflow.chain`

The adapter that appends contributed workflows to a type's configured chain.

```{eval-rst}
.. autosummary::

    chain.additional_workflows_chain
```

## `collective.multiworkflow.utils.workflow`

The values the `workflow_states` catalog index holds, and the helpers that build and read them.

```{eval-rst}
.. autosummary::

    utils.workflow.WORKFLOW_STATES
    utils.workflow.STATE_SEPARATOR
    utils.workflow.format_state
    utils.workflow.parse_state
    utils.workflow.formatted_workflow_states
```

## `collective.multiworkflow.indexers.workflow_states`

The indexer that fills the `workflow_states` catalog index.

```{eval-rst}
.. autosummary::

    indexers.workflow_states.workflow_states
```

## `collective.multiworkflow.subscribers.reindex`

The event subscriber keeping the index fresh for workflows with a state variable of their own.

```{eval-rst}
.. autosummary::

    subscribers.reindex.reindex_workflow_states
```

## `collective.multiworkflow.querystring`

Rewriting of `review_state` queries onto the chain index.

```{eval-rst}
.. autosummary::

    querystring.query_index_modifiers.qualify
    querystring.query_index_modifiers.ReviewStateModifier
```

## `collective.multiworkflow.vocabularies`

```{eval-rst}
.. autosummary::

    vocabularies.workflow.WorkflowStatesVocabulary
```

## `collective.multiworkflow.restapi.serializer`

A patch to `plone.restapi`'s content serializer, and the summary metadata, adding `workflow_states` to the payloads.
The patch is applied when the package's ZCML is loaded; nothing here is called directly.

```{eval-rst}
.. autosummary::

    restapi.serializer.dxcontent.apply_patch
    restapi.serializer.summary.JSONSummarySerializerMetadata
```

## `collective.multiworkflow.exportimport`

A patch to `plone.exportimport`, so that imported content has the role mappings and chain index entries of the state it was imported in.
Applied when the package's ZCML is loaded; nothing here is called directly.

```{eval-rst}
.. autosummary::

    exportimport.update_role_mappings
    exportimport.reindex_workflow_variables
    exportimport.apply_patches
```
