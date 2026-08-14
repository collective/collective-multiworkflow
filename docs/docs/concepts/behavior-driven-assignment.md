---
myst:
  html_meta:
    "description": "Why workflows are assigned through behaviors rather than through per-type chain configuration."
    "property=og:description": "Why workflows are assigned through behaviors rather than through per-type chain configuration."
    "property=og:title": "About behavior-driven assignment"
    "keywords": "Plone, collective.multiworkflow, behavior, adapter, IWorkflowChain, subscription adapter"
---

(concepts-behavior-driven-assignment)=

# About behavior-driven assignment

A chain could be extended by editing a content type's configuration.
This package extends it through behaviors instead.
This page explains why, and how the mechanism arranges for that without disturbing anything else.

## Why a behavior

A behavior is Plone's existing answer to the question "how do I give some content types an optional capability?"
It is enabled per type, discoverable in the types control panel, shipped in a profile, and already the unit in which integrators think about optional features.

Assigning workflows the same way inherits all of that.
A behavior that means "this content is also a membership record" can carry the membership workflow with it, so enabling the behavior and gaining the workflow are one act rather than two that can fall out of step.

The alternative, editing the chain of the `Document` type, has no way to say *which* documents, and no way to keep the workflow and the reason for the workflow together.

## How the chain adapter wins

Plone resolves a chain through an `IWorkflowChain` adapter, and its default adapter is registered for `Interface`, that is, for everything.

This package registers its own adapter for `IAdditionalWorkflows`, the base marker every participating behavior's marker extends.
A more specific registration wins, so participating content gets this package's adapter and every other object in the site keeps resolving through Plone's, unchanged.

The adapter computes the base chain by calling Plone's default adapter *function* directly rather than by asking the tool again.
That function reads the tool's own `_chains_by_type` mapping, so the call cannot re-enter adapter lookup and there is no recursion to guard against.

It then appends, never replaces.
The type's configured chain always leads, which is what makes "the first workflow drives `review_state`" a rule the rest of the package can rely on.

## Why contributions are subscription adapters

The workflows a marker contributes are registered as a **subscription** adapter, not a plain one.

A plain adapter has exactly one winner per interface, so an object providing two participating behaviors would gain the workflows of only one of them.
Subscribers all fire, and their results are concatenated in registration order and deduplicated, so an object providing several participating markers collects the contributions of all of them.

That matters as soon as behaviors compose, which is the normal case in a real site.

## Failing loudly, and failing quietly, in the right places

The package chooses a different failure mode at each end of the mechanism.

At configuration time, a marker that does not extend `IAdditionalWorkflows` raises `ConfigurationError` and the site does not start.
Such a marker would leave the adapter inapplicable and the contribution silently ignored, so a loud failure while the ZCML is being read is strictly better than a working site that quietly does nothing.

At runtime, a contributed workflow id that no workflow answers to is logged and skipped.
Chain lookup happens on every access to the object, and raising there would make the object unusable rather than merely misconfigured.

```{seealso}
{doc}`/reference/zcml` for the directive, and {doc}`/how-to-guides/declare-additional-workflows` for the steps.
```
