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
    The title is the label declared for the workflow on the backend, when there is one.

`AdditionalWorkflowMenu`
:   Renders the transitions of one additional workflow as a menu.

`StateBadge`
:   A compact label for one workflow's current state, for use in listings.
    It renders from either shape the backend serves, and takes an optional `className` with both.
    Given an `entry`, one chain entry of the `@workflow` payload, it shows the translated state title, with the workflow's title in the `title` attribute.
    Given a `value`, one `workflow_states` value of a content object or a catalog summary, it shows the optional translated `label`, or the state id when there is none.
    A value with no separator renders nothing.
    A listing can use `value` with no `@workflow` request per item.
    Either way it emits `data-workflow` and `data-state` attributes carrying the stable ids, which is what styling and acceptance tests should key on rather than the translated titles.

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
:   Maps every workflow id in a chain to its translated title, which is the label declared for the workflow when there is one.
    History entries carry only `workflow_id`, so a view that labels them reads the chain as well.

`getWorkflowStates(item?)`
:   The `workflow_states` values of a content object or a catalog summary, in chain order.
    Empty when the item carries no such key.

`getAdditionalWorkflowStates(item?)`
:   Every `workflow_states` value after the first—the states of the additional workflows.

`parseWorkflowState(value)`
:   Splits a `workflow_states` value into `workflow_id` and `state_id`.
    `undefined` for a value with no separator.

`formatWorkflowState(workflowId, stateId)`
:   Builds a `workflow_states` value out of the two ids.

## Constants

`WORKFLOW_STATE_SEPARATOR`
:   The `|` separating the workflow id from the state id within a `workflow_states` value.

`WORKFLOW_STATES_VOCABULARY`
:   The name of the backend vocabulary holding one term per state of every workflow.
    Its tokens are `workflow_states` values, and its titles read `<workflow>: <state>`, naming the workflow by any label declared for it.
    Anyone who can view the context can read it, so it is where a listing takes the `label` of a value from.

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

`WorkflowState`, `WorkflowTransition`, `WorkflowChainEntry`, `WorkflowInfo`, `HistoryEntry`, `MultiWorkflowState`, `WorkflowStateValue`, `ParsedWorkflowState`, and `WithWorkflowStates` are exported from the package root.

They mirror the backend serializer exactly and are the single source of truth for consumers.
They must be updated in the same commit as any serializer change.
