---
myst:
  html_meta:
    "description": "Why collective.multiworkflow works the way it does: chains, behaviors, state variables, permissions, and the catalog index."
    "property=og:description": "Why collective.multiworkflow works the way it does: chains, behaviors, state variables, permissions, and the catalog index."
    "property=og:title": "Concepts"
    "keywords": "Plone, collective.multiworkflow, concepts, explanation, workflow"
---

(concepts-index)=

# Concepts

This part of the documentation explains why the package works the way it does.
It is discursive rather than instructional; for directions toward a result, see {doc}`/how-to-guides/index`.

```{toctree}
:maxdepth: 1
:hidden: true

workflow-chains
behavior-driven-assignment
state-variables
permissions
the-workflow-states-index
scope
```

{doc}`workflow-chains`
:   What a chain is, why chains were impractical before, and what this package changes.
    Start here.

{doc}`behavior-driven-assignment`
:   Why workflows are assigned through behaviors, and how the chain adapter applies to participating content alone.

{doc}`state-variables`
:   Why `review_state` belongs to the publication workflow, and why additional workflows share one other name.

{doc}`permissions`
:   The one constraint concurrent workflows must satisfy, and why an overlap is reported rather than resolved.

{doc}`the-workflow-states-index`
:   Why one catalog index describes a whole chain, and why existing `review_state` queries are rewritten onto it.

{doc}`scope`
:   What the package deliberately does not do.

```{seealso}
The Diátaxis framework calls this class of documentation [explanation](https://diataxis.fr/explanation/).
```
