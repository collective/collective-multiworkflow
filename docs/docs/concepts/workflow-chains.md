---
myst:
  html_meta:
    "description": "What a workflow chain is in Plone, why chains were rarely used, and what this add-on changes."
    "property=og:description": "What a workflow chain is in Plone, why chains were rarely used, and what this add-on changes."
    "property=og:title": "About workflow chains"
    "keywords": "Plone, collective.multiworkflow, workflow, chain, portal_workflow"
---

(concepts-workflow-chains)=

# About workflow chains

Plone's `portal_workflow` has always allowed more than one workflow to be active on the same content object at the same time.
This page explains what that means, why almost nobody used it, and what this add-on changes.

## What a chain is

A **chain** is the ordered tuple of workflows that apply to one object.
`portal_workflow` resolves it through an `IWorkflowChain` adapter, and Plone's default adapter answers with the chain configured for the object's content type—usually a single workflow, most often `simple_publication_workflow`.

Nothing in the tool requires that tuple to hold one entry.
When it holds several, each workflow keeps its own status record on the object, its own states, its own transitions, and its own role mappings.
They run concurrently: no workflow in the chain is subordinate to another, and a transition in one does not trigger a transition in another.

That last point is worth stating plainly, because the word *chain* suggests otherwise.
A chain is a set of workflows that happen to apply to the same object, not a pipeline.

## Why chains were impractical

Three obstacles, none of them in the workflow tool itself.

**Assignment was per type, and manual.**
`portal_workflow` maps a chain to a *content type*, so the unit of configuration is `Document`, not "documents that are also membership records."
Adding a second workflow meant editing the chain of a type through the ZMI or a GenericSetup profile, and every object of that type got it whether it made sense or not.

**Everything reads `review_state`.**
A second workflow written the obvious way declares `review_state` as its state variable too, and the two immediately fight: the catalog holds one value, the publication menu shows the wrong transitions, and `plone.api.content.get_state` answers for whichever workflow the tool consulted first.

**The surrounding machinery only ever looks at one workflow.**
The catalog indexes `review_state` and nothing else.
`plone.restapi`'s `@workflow` reports the effective state; its `@history` reads `review_history` without naming a workflow, and so returns the first workflow's history and silently omits the rest.
A second workflow could therefore be configured and still be invisible to search, to the REST API, and to the user interface.

## What this add-on changes

It addresses the three obstacles in turn.

**Assignment moves to behaviors.**
A behavior declares the workflows it contributes, and any content type enabling that behavior gains them.
The unit of configuration becomes the behavior, which is already how Plone composes optional capabilities onto types.
See {doc}`behavior-driven-assignment`.

**`review_state` is left alone.**
Each additional workflow declares a state variable of its own, so the publication workflow keeps answering for `review_state` exactly as before.
See {doc}`state-variables`.

**The machinery is taught to see the whole chain.**
One catalog index describes every workflow's state; the `@workflow` endpoint gains a per-workflow breakdown; `@history` reports every workflow's transitions, each tagged with the workflow that recorded it; and the Volto components render each additional workflow alongside the publication one.

## What stays as it was

The chain configured for a content type is never replaced.
Contributed workflows are appended after it, so the first workflow of any chain is still the one the type was configured with, and still the one driving `review_state`.
When several behaviors contribute, {ref}`reference-zcml-order` gives the order their workflows follow in.

Content that provides no participating behavior is not touched at all.
Its chain resolution, its catalog entries, and its REST API payloads are exactly what they were before the add-on was installed.

```{seealso}
{doc}`permissions` for the one constraint two concurrent workflows must satisfy, and {doc}`scope` for what this package deliberately does not do.
```
