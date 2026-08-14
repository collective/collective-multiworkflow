---
myst:
  html_meta:
    "description": "The components, helpers, actions, and types the volto-multiworkflow add-on exports."
    "property=og:description": "The components, helpers, actions, and types the volto-multiworkflow add-on exports."
    "property=og:title": "Volto add-on"
    "keywords": "Plone, collective.multiworkflow, Volto, React, components, Redux"
---

(reference-frontend)=

# Volto add-on

The frontend package is `@plone-collective/volto-multiworkflow`.
It renders the additional workflows of the current content object, and renders nothing at all on content that has none.

Every payload shape named here is described in {doc}`rest-api`.

## Customizations

The add-on shadows two core components.

`volto/components/manage/Workflow/Workflow`
:   Puts each additional workflow's state and transitions in the same control as the publication workflow, rather than in a separate menu.

`volto/components/manage/History/History`
:   Renders the merged history, naming the workflow of each entry when the history spans more than one.

Neither shadow changes what the component renders for content without additional workflows.

## Components

`AdditionalWorkflow`
:   Renders one additional workflow: its title, its current state, and the transitions available to the user.

`AdditionalWorkflowMenu`
:   Renders the transitions of one additional workflow as a menu.

`StateBadge`
:   A compact label for one workflow's current state, for use in listings.
    Takes an `entry` prop—one chain entry—and an optional `className`.
    It emits `data-workflow` and `data-state` attributes carrying the stable ids, which is what styling and acceptance tests should key on rather than the translated titles.

## Helpers

`getPrimaryWorkflow(chain?)`
:   The first chain entry, the one driving `review_state`.
    `undefined` when the chain is empty or absent.

`getAdditionalWorkflows(chain?)`
:   Every entry after the first—the additional workflows.
    Empty for content that does not use this add-on.

`hasAdditionalWorkflows(chain?)`
:   Whether there is any additional workflow worth rendering.

`threadPreviousStates(entries)`
:   Fills in each history entry's `prev_state_title`, per workflow.
    A merged history breaks the assumption that entry *N-1* is the previous state of entry *N*, because the preceding entry usually belongs to a different workflow.
    Entries are taken and returned newest first.

`markCurrentVersion(entries)`
:   Sets `is_current` on the newest versioning entry.

`spansMultipleWorkflows(entries)`
:   Whether a history mixes entries from more than one workflow.
    The History view uses this to decide whether naming the workflow is worth a column.

`getWorkflowTitles(chain?)`
:   Maps every workflow id in a chain to its translated title.
    History entries carry only `workflow_id`, so a view that labels them reads the chain as well.

## Actions

`getMultiWorkflow(url)`
:   Fetches the full `@workflow` payload, including `chain`.

`transitionMultiWorkflow(transitionUrl)`
:   Executes a transition by posting to the `@id` reported for it.

```{important}
Both actions exist because core's workflow reducer keeps only `state`, `history`, and `transitions` from the `@workflow` response, so `chain` never reaches the store.

A transition's response is the last `review_history` entry, not a workflow payload, so the chain must be re-fetched after a successful transition.
```

## Store

The add-on installs one reducer under `multiworkflow`.

| Key | Type | Meaning |
|---|---|---|
| `loading` | `boolean` | a request is in flight |
| `loaded` | `boolean` | the last request succeeded |
| `error` | `unknown \| null` | the last failure, if any |
| `chain` | `WorkflowChainEntry[]` | the current object's chain; empty when it has none |

Content without additional workflows reduces to an empty `chain`, so a consumer can render nothing without special-casing the absent key.

## Types

`WorkflowState`, `WorkflowTransition`, `WorkflowChainEntry`, `WorkflowInfo`, `HistoryEntry`, and `MultiWorkflowState` are exported from the package root.

They mirror the backend serializer exactly and are the single source of truth for consumers.
They must be updated in the same commit as any serializer change.
