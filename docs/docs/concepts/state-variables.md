---
myst:
  html_meta:
    "description": "Why an additional workflow must never drive review_state, and why one shared state variable name is recommended instead."
    "property=og:description": "Why an additional workflow must never drive review_state, and why one shared state variable name is recommended instead."
    "property=og:title": "About state variables and review_state"
    "keywords": "Plone, collective.multiworkflow, review_state, state variable, DCWorkflow, catalog"
---

(concepts-state-variables)=

# About state variables and `review_state`

Every workflow records the state of an object in a variable of its own, named by its `state_variable` setting.
Plone's publication workflow names it `review_state`, and so much of Plone reads that name that it is easy to mistake it for the name of the concept rather than the name of one workflow's variable.

This page explains why an additional workflow must not use it, and why this package recommends that additional workflows share one other name instead.

## Status is keyed by workflow, not by variable

DCWorkflow stores an object's workflow status in a mapping keyed by **workflow id**.
Each workflow's record is separate, and each record holds that workflow's own state under that workflow's own variable name.

Two consequences follow, and the second one surprises people.

- Two workflows in a chain cannot corrupt each other's stored state, whatever they call their variables.
- Two workflows in a chain may therefore use the *same* variable name without colliding, because the name is only ever read inside one workflow's record.

## Why `review_state` must stay with the publication workflow

Not because of storage, then, but because of everything reading it.

`review_state` is the name the catalog indexes, the name `plone.api.content.get_state` returns, the name the sharing and publication user interface acts on, and the name `WorkflowTool.getInfoFor` resolves when no workflow is specified—by walking the chain and answering with the first workflow that declares it.

An additional workflow declaring `review_state` therefore does not overwrite the publication workflow's state.
It does something harder to debug: it makes the *answer to an unqualified question* depend on chain order.
Content appears published because a membership workflow happens to have a state of that name, or a publication transition disappears from a menu because another workflow answered first.

So the rule is not a matter of taste.
An additional workflow declaring `review_state` is a bug, and the only reliable way to keep `review_state` meaning what it has always meant is to leave it to the workflow that owns it.

## Why one shared name for the rest

This package recommends that every additional workflow declare the same name as the catalog index, `workflow_states`, as its state variable.

The reason is mechanical.
`WorkflowTool._reindexWorkflowVariables` reindexes exactly those catalog indexes named after a workflow variable in the object's chain.
A workflow whose state variable is `workflow_states` therefore keeps the `workflow_states` index fresh on every transition, at no cost and with no subscriber involved.

A workflow that keeps a bespoke variable—one written before this index existed, say—is not broken by that choice.
It is covered instead by an event handler that reindexes after a transition, and only when nothing else will.
The handler exists precisely so that the recommendation stays a recommendation.

Sharing the name across several workflows is safe, for the reason given above: the name is read inside one workflow's record at a time.

```{important}
The catalog value never comes from the workflow variable that shares the index's name.
`plone.indexer`'s wrapper consults `IIndexer` adapters before it consults workflow variables, so the index always holds what this package's indexer computed: every workflow in the chain, in order.
```

## What a reader should take away

- `review_state` is one workflow's variable, not a general concept.
- An additional workflow must declare its own state variable, and `workflow_states` is the one to declare.
- Reading a specific workflow's state means naming that workflow, which is what {doc}`the Python API </reference/api/api>` and the `chain` key of the REST API both make possible.

```{seealso}
{doc}`/how-to-guides/write-a-composing-workflow` for the steps, and {doc}`/reference/catalog` for what the index holds.
```
