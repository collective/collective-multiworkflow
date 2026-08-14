---
myst:
  html_meta:
    "description": "Read an object's state in a specific workflow and execute a transition belonging to it."
    "property=og:description": "Read an object's state in a specific workflow and execute a transition belonging to it."
    "property=og:title": "How to read and transition workflow state"
    "keywords": "Plone, collective.multiworkflow, plone.api, get_state, transition"
---

(howto-read-and-transition-state)=

# How to read and transition workflow state

This guide shows you how to read an object's state in a specific workflow, and how to execute a transition belonging to one.

`collective.multiworkflow.api` is a superset of the `plone.api` workflow helpers.
Called without a `workflow_id`, every function here behaves exactly as its `plone.api` counterpart, reading and driving `review_state`.
You can therefore import it in place of `plone.api.content` and change nothing else.

## Prerequisites

- Content participating in at least one additional workflow.

## Read one workflow's state

Pass `workflow_id` to address a specific workflow in the chain.

```python
from collective.multiworkflow import api as mw_api

membership = mw_api.get_state(
    obj, workflow_id="foundation_member_workflow"
)
```

Omit it to read `review_state`, exactly as before.

```python
publication = mw_api.get_state(obj)
```

Pass `default` to get a value back instead of an exception when the object has no workflow at all.

```python
state = mw_api.get_state(obj, default=None)
```

An unknown `workflow_id` raises `InvalidParameterError`.

## Read the whole chain at once

```python
states = mw_api.get_states(obj)
```

The result maps workflow id to state id, in chain order.

```python
{
    "simple_publication_workflow": "private",
    "foundation_member_workflow": "active",
}
```

## List the available transitions

```python
available = mw_api.transitions(obj)
```

The result maps workflow id to the ids of that workflow's transitions available to the **current user**.
Workflows with nothing available are omitted, so a missing key means the workflow has nothing to offer, not that no such workflow exists.

```python
{
    "simple_publication_workflow": ["publish", "submit"],
    "foundation_member_workflow": ["activate"],
}
```

## Execute a transition

```python
mw_api.transition(
    obj, "activate", workflow_id="foundation_member_workflow"
)
```

Without `workflow_id`, the transition is routed exactly as `plone.api.content.transition` routes it: the first workflow in the chain that supports the id wins.

Pass `workflow_id` when the transition id is shadowed by an earlier workflow in the chain, or whenever you want to be explicit about which workflow you are driving.
Keyword arguments are passed through to the workflow, so a comment works as it always has.

```python
mw_api.transition(
    obj,
    "activate",
    workflow_id="foundation_member_workflow",
    comment="Renewed for 2026",
)
```

An invalid transition raises `InvalidParameterError`, with the valid transitions of that workflow listed in the message.

```{important}
`to_state` cannot be combined with `workflow_id`.
Targeting a state rather than a transition is only meaningful for the publication workflow; name the transition explicitly for anything else.
```

## Find which workflow owns a transition

```python
owners = mw_api.owning_workflow(obj)
```

The result maps every transition id in the chain to the workflow that owns it.
An id defined by more than one workflow is attributed to the first in chain order, which is how `doActionFor` resolves the same collision.

```{seealso}
{doc}`/reference/api/api` for the complete signatures.
```
