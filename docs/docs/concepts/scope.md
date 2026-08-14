---
myst:
  html_meta:
    "description": "What this package deliberately does not do, and why each exclusion is deliberate."
    "property=og:description": "What this package deliberately does not do, and why each exclusion is deliberate."
    "property=og:title": "About the scope of this package"
    "keywords": "Plone, collective.multiworkflow, scope, placeful workflow, sub-workflow"
---

(concepts-scope)=

# About the scope of this package

Four things a reader might reasonably expect are out of scope.
Each is excluded for a reason worth stating, because in every case the exclusion is a design position rather than an unfinished feature.

## Placeful workflows

`CMFPlacefulWorkflow` makes the chain depend on *where* an object lives.
This package makes it depend on *what* the object is.

The two are not in conflict, but they resolve the chain through the same adapter, and a combined answer would need a policy for which one wins where.
This package does not integrate with placeful workflows and does not define such a policy.

## Sub-workflows

A transition in one workflow triggering a transition in another is not supported, and is not a missing feature.

The chain model is concurrent by construction: the workflows in a chain are peers, none subordinate to another, and this is exactly what keeps them from interfering.
A hierarchy would reintroduce the coupling the model exists to avoid.
Where one workflow really must respond to another, an event subscriber on the transition event is the place for it—outside the chain, where the dependency is visible.

## Reconciling workflows that manage the same permission

Two workflows managing the same permission is reported, never arbitrated.
{doc}`permissions` gives the argument in full: there is no correct merge, and a silent resolution would hide a design error that a person needs to see.

## Any change to `review_state` semantics

`review_state` keeps meaning what it has always meant: the state of the workflow the content type is configured with.

Nothing in this package widens it, redirects it, or makes it aggregate several workflows.
Every mechanism here is additive precisely so that code, indexes, and clients written before the package existed keep behaving as they did.
{doc}`state-variables` explains why that boundary is worth defending.

```{seealso}
{doc}`workflow-chains` for what the package does do.
```
