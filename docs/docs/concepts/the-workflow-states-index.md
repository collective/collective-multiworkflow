---
myst:
  html_meta:
    "description": "Why one catalog index describes a whole workflow chain, and why review_state queries are rewritten onto it."
    "property=og:description": "Why one catalog index describes a whole workflow chain, and why review_state queries are rewritten onto it."
    "property=og:title": "About the workflow_states index"
    "keywords": "Plone, collective.multiworkflow, catalog, index, collection, review_state"
---

(concepts-the-workflow-states-index)=

# About the `workflow_states` index

A site whose content participates in several workflows has to be able to find that content by any of their states.
This page explains the shape chosen for that, and the consequence it has for queries written before the package existed.

## One index, not one per workflow

The obvious design gives each additional workflow its own index, named after its state variable.
This package uses a single `KeywordIndex` describing the whole chain instead.

The reason is growth.
Behaviors are added over a site's lifetime, and an index-per-workflow design means the catalog grows a new index every time someone enables one—each needing a profile step, an upgrade step, and a reindex.
One index for the chain means a site's catalog schema stops changing after the add-on is installed, whatever behaviors arrive later.

The cost is that values must carry their workflow with them, hence `<workflow-id>|<state-id>`.
A `KeywordIndex` holds several values per object naturally, so an object in three workflows is three entries and any of them can be queried.

## Why chain order is part of the contract

The index holds its values in chain order, and the first value is always the workflow driving `review_state`, for every object, whether or not anything was contributed to it.

The indexer is registered for all content rather than for participating content alone, which is what makes that guarantee hold site-wide.
A caller can therefore read entry zero without first asking whether the object participates, and code that wants "the publication state" has one rule rather than two.

## Why one of the three maintenance paths is a patch

An index is only as good as whatever keeps it current, and an object's state can change in three ways.
Two of them are events: a transition, which Plone already reindexes for, and a transition on a workflow with a bespoke state variable, which this package's own subscriber covers.

The third is import, and it is not an event at all.
`plone.exportimport` restores an object's state by assigning `workflow_history` directly, which is the correct thing to do (a real transition would invent history and run the transition's guards and scripts) and which fires nothing.
So neither of the first two mechanisms runs, and the imported object keeps the catalog entry it was created with.
It keeps the role mappings of that initial state too, since applying a state's permission map is also something only a transition does.

There is no subscriber to register for that, because nothing is notified.
The only place to act is inside the importer, which is why this package patches `plone.exportimport` rather than adding a third listener.
The patch is deliberately generic: it reapplies the permission map of each workflow's restored state and reindexes whatever the object's workflow variables are named, so it is the change this package would like to see upstream, not a special case for one index.

What makes the bug worth this trouble is the shape of it.
`review_state` is imported by a real transition, so the publication half of the index is always right, and imported content looks healthy under exactly the spot-check anyone would perform.
Only the additional workflow is stale, and only in the catalog: the object itself is correct, so a debugging session that reads the object rather than querying for it finds nothing wrong.

## Why `review_state` queries are rewritten

A site installing this add-on already has collections, saved searches, and code querying `review_state` with values like `published`.

Those queries still have an index to answer them.
The stock `review_state` index is maintained exactly as before, by whichever workflow drives each object's `review_state`, so a bare `published` finds what it always found.
What it cannot do is name an additional workflow: the collection editor offers every state of every workflow as a qualified value, and only `workflow_states` holds those.

So a parsed `review_state` query is moved onto `workflow_states` only when one of its values names a workflow, and is left where it is otherwise.

Moving every query and qualifying a bare state id with the site's default workflow would look equivalent, but it answers correctly only for content types driven by that workflow.
A type configured with another one would drop out of the results, and an empty result reads as *no content is in that state*, not as *this query can no longer work*.
That is the worst available failure: silent, plausible, and indistinguishable from a true answer.

When a query does move, the rewriting is deliberately conservative: it renames the index, qualifies a bare state id only when the query mixes it with qualified ones, and passes every other key of the parsed query through untouched, because those keys carry the operator of an *all of* criterion and the negation of an *excludes* one.

The result is that an existing query keeps meaning what its author meant, and a new one can name any workflow it likes.

```{seealso}
{doc}`/reference/catalog` for the exact rules, and {doc}`/how-to-guides/search-by-workflow-state` for how to write a query.
```
