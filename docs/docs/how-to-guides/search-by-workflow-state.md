---
myst:
  html_meta:
    "description": "Query content by its state in any workflow of the chain, from code and from a collection."
    "property=og:description": "Query content by its state in any workflow of the chain, from code and from a collection."
    "property=og:title": "How to search by an additional workflow state"
    "keywords": "Plone, collective.multiworkflow, catalog, search, collection, workflow_states"
---

(howto-search-by-workflow-state)=

# How to search by an additional workflow state

This guide shows you how to find content by its state in any workflow of its chain.

## Prerequisites

- The add-on installed, and content in at least one additional workflow.

## Query the index from code

Query `workflow_states`, building the value with `format_state`.

```python
from collective.multiworkflow.utils.workflow import format_state
from plone import api

active = api.content.find(
    workflow_states=format_state("foundation_member_workflow", "active")
)
```

`workflow_states` is a `KeywordIndex`, so a list of values matches any of them.

```python
results = api.content.find(
    workflow_states=[
        format_state("foundation_member_workflow", "active"),
        format_state("foundation_member_workflow", "pending"),
    ]
)
```

To require several states at once—published *and* an active member—pass the `and` operator.

```python
results = api.content.find(
    workflow_states={
        "query": [
            format_state("simple_publication_workflow", "published"),
            format_state("foundation_member_workflow", "active"),
        ],
        "operator": "and",
    }
)
```

## Read a value back

Use `parse_state` rather than splitting the string yourself.

```python
from collective.multiworkflow.utils.workflow import parse_state

for brain in active:
    for value in brain.workflow_states:
        workflow_id, state_id = parse_state(value)
```

The metadata column is available on brains, so this needs no object wake-up.
Values are in chain order, and the first is always the workflow driving `review_state`.

## Read the states from a search request

Summaries of catalog results carry `workflow_states`, so a search returns every item's states with no further request.

```http
GET /plone/@search?portal_type=Profile HTTP/1.1
Accept: application/json
```

Each item of the response holds a `workflow_states` list, in the same format and order as the index.
The serialization of a single object carries the same key.
See {ref}`reference-rest-api-content`.

## Add a criterion to a collection

In the collection editor, choose the **Review state** criterion.
Its vocabulary lists every state of every registered workflow, titled `<workflow>: <state>`, so an additional workflow's states are selectable there with no further configuration.

## What happens to existing `review_state` criteria

A criterion written before the add-on was installed keeps working.

Parsed `review_state` queries are redirected onto `workflow_states`, and a bare state id such as `published` is qualified with the first workflow of the site's default chain.
The operator of an *all of* criterion and the negation of an *excludes* criterion are preserved.

You do not need to rewrite stored collections.

```{note}
Code that queries `review_state` through `portal_catalog` directly is *not* rewritten—only parsed collection queries pass through the modifier.
Direct catalog queries against `review_state` continue to work, because the stock `review_state` index is still there and still maintained by the publication workflow.
```

## If a query returns nothing

Check that the index is populated.

```python
catalog = api.portal.get_tool("portal_catalog")
assert catalog.Indexes["workflow_states"].numObjects() > 0
```

An empty index on a site with content means the objects were never indexed under it—see {doc}`add-to-an-existing-site`.

```{seealso}
{doc}`/reference/catalog` for the exact rules, and {doc}`/concepts/the-workflow-states-index` for why they are these rules.
```
