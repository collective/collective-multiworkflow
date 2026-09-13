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
when-to-use
```

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} Workflow chains
:link: workflow-chains
:link-type: doc

What a chain is, why chains were impractical before, and what this package changes.
+++
Start here.
````

````{grid-item-card} Behavior-driven assignment
:link: behavior-driven-assignment
:link-type: doc

Why workflows are assigned through behaviors, and how the chain adapter applies to participating content alone.
````

````{grid-item-card} State variables
:link: state-variables
:link-type: doc

Why `review_state` belongs to the publication workflow, and why additional workflows share one other name.
````

````{grid-item-card} Permissions
:link: permissions
:link-type: doc

The one constraint concurrent workflows must satisfy, and why an overlap is reported rather than resolved.
````

````{grid-item-card} The workflow_states index
:link: the-workflow-states-index
:link-type: doc

Why one catalog index describes a whole chain, and why existing `review_state` queries are rewritten onto it.
````

````{grid-item-card} Scope
:link: scope
:link-type: doc

What the package deliberately does not do.
````

````{grid-item-card} When an additional workflow fits
:link: when-to-use
:link-type: doc

The kind of problem the package solves, three scenarios it fits, and the signs of one it does not.
````
`````

```{seealso}
The Diátaxis framework calls this class of documentation [explanation](https://diataxis.fr/explanation/).
```
