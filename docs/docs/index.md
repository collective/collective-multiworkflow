---
myst:
  html_meta:
    "description": "Assign additional workflows to content types through behaviors, with full support in plone.restapi and Volto."
    "property=og:description": "Assign additional workflows to content types through behaviors, with full support in plone.restapi and Volto."
    "property=og:title": "Multi-Workflow Support for Plone"
    "keywords": "Plone, collective.multiworkflow, workflow, chain, behavior, Volto"
---

# Multi-Workflow Support for Plone

<div align="center">

[![Built with Cookieplone](https://img.shields.io/badge/built%20with-Cookieplone-0083be.svg?logo=cookiecutter)](https://github.com/plone/cookieplone-templates/)


[![PyPI](https://img.shields.io/pypi/v/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)
[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)


[![npm](https://img.shields.io/npm/v/@plone-collective/volto-multiworkflow)](https://www.npmjs.com/package/@plone-collective/volto-multiworkflow)
[![Storybook](https://img.shields.io/badge/-Storybook-ff4785?logo=Storybook&logoColor=white&style=flat-square)](https://collective.github.io/collective-multiworkflow/storybook/)


[![GitHub contributors](https://img.shields.io/github/contributors/collective/collective-multiworkflow)](https://github.com/collective/collective-multiworkflow)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/collective-multiworkflow?style=social)](https://github.com/collective/collective-multiworkflow)

[![CI](https://github.com/collective/collective-multiworkflow/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective-multiworkflow/actions/workflows/main.yml)

</div>

`collective.multiworkflow` lets a behavior add workflows to a content type's workflow chain, and carries those workflows through the catalog, the REST API, and Volto.

When a content type provides a participating behavior, this add-on **appends** one or more workflows to that type's chain.
The chain configured for the type is never replaced, `review_state` never changes meaning, and content that does not provide the behavior is left completely untouched.

```python
from collective.multiworkflow import api as mw_api

mw_api.get_states(member)
```

```python
{'simple_publication_workflow': 'published', 'membership_workflow': 'active'}
```

```{warning}
This documentation was written with Claude Opus 5, following the [Plone documentation style skill](https://github.com/plone/plone-doc-style-skill), and reviewed by a human being.
```

## Where to start

`````{grid} 1 1 2 2
:gutter: 3

Not sure an additional workflow is the right tool for your problem?
{doc}`concepts/when-to-use` describes the problems it fits, and the signs of one it does not.

````{grid-item-card} 🎓 Tutorial
:link: tutorials/add-a-second-workflow
:link-type: doc

Give a content type a second workflow and drive it end to end.
+++
Start here if the package is new to you.
````

````{grid-item-card} 🛠️ How-to guides
:link: how-to-guides/index
:link-type: doc

Install the package, declare a contribution, search by an additional state.
+++
Directions toward a result.
````

````{grid-item-card} 💡 Concepts
:link: concepts/index
:link-type: doc

Why chains, why behaviors, why `review_state` is left alone.
+++
Understanding, away from the keyboard.
````

````{grid-item-card} 📖 Reference
:link: reference/index
:link-type: doc

The Python API, the ZCML directive, the catalog index, the REST API, Volto.
+++
Technical description of the machinery.
````
`````

## What it gives you

**Behavior-driven assignment.**
Enable a behavior on a type and its workflows come along.
No per-type chain editing, and no workflow on content that should not have it.

**`review_state` untouched.**
Each additional workflow drives a state variable of its own, so Plone's publication workflow keeps working exactly as before.

**Workflow-aware helpers.**
Read and drive per-workflow state with `plone.api`-style functions whose defaults behave identically to the API you already use.

**One catalog index for the whole chain.**
Additional states are queryable like any other index, and existing `review_state` collections keep working.

**REST API and Volto.**
`@workflow` gains a per-workflow breakdown, `@history` reports every workflow's transitions tagged with the workflow that recorded them, and the Volto components render each additional workflow—or nothing at all, on content that has none.

## What is not in scope

Placeful workflows, sub-workflows, and any arbitration between workflows managing the same permission.
{doc}`concepts/scope` explains why each exclusion is deliberate.

```{toctree}
:caption: Tutorials
:maxdepth: 2
:hidden: true

tutorials/index
```

```{toctree}
:caption: How-to guides
:maxdepth: 2
:hidden: true

how-to-guides/index
```

```{toctree}
:caption: Concepts
:maxdepth: 2
:hidden: true

concepts/index
```

```{toctree}
:caption: Reference
:maxdepth: 2
:hidden: true

reference/index
```

```{toctree}
:caption: Appendices
:maxdepth: 2
:hidden: true

glossary
genindex
```
