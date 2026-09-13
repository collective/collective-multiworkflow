---
myst:
  html_meta:
    "description": "The workflow_states catalog index, the values it holds, and how review_state queries are rewritten onto it."
    "property=og:description": "The workflow_states catalog index, the values it holds, and how review_state queries are rewritten onto it."
    "property=og:title": "Catalog index"
    "keywords": "Plone, collective.multiworkflow, catalog, index, workflow_states, collection"
---

(reference-catalog)=

# Catalog index

The `default` profile adds one `KeywordIndex` named `workflow_states` to `portal_catalog`, along with a metadata column of the same name.
One index describes an object's whole chain, so a site gains no further indexes as behaviors contribute more workflows.

```{seealso}
{doc}`api/utils`, {doc}`api/indexers`, {doc}`api/subscribers`, and {doc}`api/querystring` for the generated API description.
```

## Indexed values

Each value reads `<workflow-id>|<state-id>`.

```text
simple_publication_workflow|private
foundation_member_workflow|active
```

The following rules hold for every indexed object.

- Values are in chain order.
  The first value is always the workflow that drives `review_state`, whether or not anything was contributed to the object.
- The separator is `|`.
  Neither a workflow id nor a state id can contain it, because both are Zope ids.
- An object with no workflow at all indexes nothing.

Build a value with `format_state`, and read one back with `parse_state`.
Do not assemble or split the string by hand.

## Metadata column

The metadata column holds the same values as the index, in the same order, so a brain carries them without waking the object up.
The REST API reads it to add `workflow_states` to every summary of a catalog result, as described in {ref}`reference-rest-api-summary`.

## The name is also a state variable

`workflow_states` is both the name of the index and the `state_variable` an additional workflow should declare.

That is not cosmetic.
`WorkflowTool._reindexWorkflowVariables` reindexes exactly the indexes named after the chain's workflow variables, so a workflow using this name keeps the index fresh with no further help.
A workflow that keeps a state variable of its own is covered instead by the `reindex_workflow_states` event handler, which reindexes only when nothing else will.

Sharing one name across several workflows is safe: DCWorkflow keys its status records by workflow id, not by variable name.

## How the index is kept fresh

Three mechanisms, covering three ways an object's state can change.

Transitions
:   `WorkflowTool._reindexWorkflowVariables` reindexes the indexes named after the chain's workflow variables.
    This covers every workflow that declares `workflow_states` as its state variable, at no cost.

The `reindex_workflow_states` event handler
:   Covers a workflow that keeps a state variable of its own, which the mechanism above would not reindex.
    It acts only when nothing else will, because a partial reindex rebuilds the object's entire metadata record.

The `plone.exportimport` patch
:   Covers content whose state arrives by import rather than by transition.
    `plone.exportimport` restores workflow state by assigning `workflow_history` directly, which fires no transition and so reaches neither mechanism above.
    See {doc}`api/exportimport`.

```{important}
What the catalog stores is always the indexer, never the workflow variable that happens to share its name.
`plone.indexer`'s wrapper consults `IIndexer` adapters before it consults workflow variables.
```

## Query rewriting

A parsed collection query against `review_state` is handled by `ReviewStateModifier`, registered as an `IParsedQueryIndexModifier`.
It moves the query to `workflow_states` only when one of its values names a workflow.

- A query none of whose values is qualified, such as `published`, stays on the stock `review_state` index, untouched.
  A stored collection written before this package was installed therefore answers exactly as it did, for every content type, whichever workflow drives its `review_state`.
- A query whose values are all qualified moves to `workflow_states`, with its values as they are.
- A query mixing bare and qualified values moves to `workflow_states`, and each bare state id is qualified with the first workflow of the site's default chain.
  The catalog intersects the results of different indexes, so splitting one criterion between the two would turn its *any of* into an *all of*.
- A value that is not a string—a date range, say—is passed through unchanged.
- When a query moves, keys other than `query` and `not` are preserved, so the `and` operator of an *all of* criterion and the negation of an *excludes* criterion both survive.

A criterion saved from the collection editor carries qualified values, because the editor offers only those, so it targets `workflow_states` from then on.
A site that declares no default chain has nothing to attribute a bare id to, and in a mixed query that value is passed through unchanged.

## Vocabulary

`collective.multiworkflow.vocabularies.WorkflowStates` provides one term per state of every registered workflow.
Terms are keyed exactly as the index holds them, and titled `<workflow title>: <state title>`.

The `default` profile makes it the value source of the existing **Review state** query field, replacing the vocabulary of plain `review_state` values.
The collection editor therefore offers every state of every workflow under the criterion editors already know, and the values it stores are qualified ones that `ReviewStateModifier` moves onto `workflow_states` untouched.
