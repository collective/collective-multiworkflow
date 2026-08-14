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
indexers
querystring
vocabularies
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
```

## `collective.multiworkflow.interfaces`

The two interfaces the mechanism is built on.

```{eval-rst}
.. autosummary::

    interfaces.IAdditionalWorkflows
    interfaces.IAdditionalWorkflowsFor
```

## `collective.multiworkflow.chain`

The adapter that appends contributed workflows to a type's configured chain.

```{eval-rst}
.. autosummary::

    chain.additional_workflows_chain
```

## `collective.multiworkflow.indexers`

The `workflow_states` catalog index and the values it holds.

```{eval-rst}
.. autosummary::

    indexers.WORKFLOW_STATES
    indexers.STATE_SEPARATOR
    indexers.format_state
    indexers.parse_state
    indexers.workflow_states
    indexers.reindex_workflow_states
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

## `collective.multiworkflow.exportimport`

A patch to `plone.exportimport`, so that importing content leaves the chain index correct.
Applied when the package's ZCML is loaded; nothing here is called directly.

```{eval-rst}
.. autosummary::

    exportimport.reindex_workflow_variables
    exportimport.apply_patches
```
