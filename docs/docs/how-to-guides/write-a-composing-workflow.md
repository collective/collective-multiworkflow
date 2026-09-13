---
myst:
  html_meta:
    "description": "Write a workflow definition that can be added to a chain without disturbing the workflow already there."
    "property=og:description": "Write a workflow definition that can be added to a chain without disturbing the workflow already there."
    "property=og:title": "How to write a workflow that composes"
    "keywords": "Plone, collective.multiworkflow, DCWorkflow, definition, state variable, permissions"
---

(howto-write-a-composing-workflow)=

# How to write a workflow that composes

This guide shows you how to write a workflow definition that can be appended to a chain without disturbing the workflow already there.

Four constraints.
Satisfy them and your workflow composes with any other that satisfies them too.

## Prerequisites

- A GenericSetup profile that ships a workflow definition, in `profiles/<name>/workflows/<workflow-id>/definition.xml`.

## 1. Declare `workflow_states` as the state variable

```xml
<dc-workflow
    workflow_id="membership_workflow"
    state_variable="workflow_states"
    title="Membership"
    >
```

Never `review_state`.
That variable belongs to the workflow your content type is configured with, and claiming it makes the answer to an unqualified state question depend on chain order.

Use `workflow_states` rather than a name of your own.
`WorkflowTool._reindexWorkflowVariables` reindexes the catalog indexes named after the chain's workflow variables, so this name keeps the `workflow_states` index fresh on every transition with no subscriber involved.

A bespoke name still works—an event handler covers it—but it costs a full metadata rebuild on each transition that the shared name avoids.

## 2. Give every transition a unique id

Transition ids must be unique across every workflow in the chains your workflow will join.

```xml
<transition transition_id="membership_activate"
            new_state="active"
            title="Activate membership"
            trigger="USER"
            />
```

`doActionFor` resolves an ambiguous id to the first workflow in the chain that defines it.
A transition named `publish` in your workflow is therefore unreachable behind the publication workflow's own `publish`, except by naming your workflow explicitly.

Prefixing ids with something specific to your domain, such as `membership_activate` rather than `activate`, is the cheapest way to guarantee this in a site whose chains you do not control.

## 3. Declare only permissions nothing else manages

If your workflow controls access, list the permissions it manages and keep that list disjoint from every other workflow in the chain.

```xml
<permission>my.package: Manage membership</permission>
```

Declaring a permission that another workflow in the chain also declares leaves the object's mapping as whichever workflow transitioned last, silently, until the other transitions or `updateRoleMappings()` runs.

The three permissions Plone's publication workflow manages are the ones to avoid by default.
Defining a permission of your own, as above, is almost always the right move.

## 4. Verify the composition

Create an object of the participating type and audit its chain.

```python
from collective.multiworkflow import api as mw_api

assert mw_api.conflicting_permissions(obj) == {}
```

An empty mapping means no permission in the chain has more than one claimant.
Anything else names the permission and the workflows fighting over it.

Then check the transition ids resolve to the workflows you expect.

```python
owners = mw_api.owning_workflow(obj)

assert owners["membership_activate"] == "membership_workflow"
```

A transition id attributed to a workflow you did not expect is a shadowing collision.
Rename it and reapply your profile.

```{seealso}
{doc}`/concepts/state-variables` and {doc}`/concepts/permissions` for why these constraints exist.
```
