---
myst:
  html_meta:
    "description": "Technical description of the Python API, the ZCML directive, the catalog index, the REST API, and the Volto add-on."
    "property=og:description": "Technical description of the Python API, the ZCML directive, the catalog index, the REST API, and the Volto add-on."
    "property=og:title": "Reference"
    "keywords": "Plone, collective.multiworkflow, reference, API"
---

(reference-index)=

# Reference

This part of the documentation describes the machinery.
It states what each part is, not how to use it.
For directions toward a result, see {doc}`/how-to-guides/index`.

```{toctree}
:maxdepth: 1
:hidden: true

api/index
zcml
catalog
rest-api
volto
profiles
```

{doc}`api/index`
:   Every public name in the Python package, generated from the source.

{doc}`zcml`
:   The `<plone:additionalworkflows />` directive: its attributes, its validation, and the errors it raises.

{doc}`catalog`
:   The `workflow_states` index: the values it holds, the order it holds them in, and how `review_state` queries are rewritten onto it.

{doc}`rest-api`
:   The additions to the `@workflow` and `@history` endpoints, with generated request and response examples.

{doc}`volto`
:   The components, helpers, actions, and types the Volto add-on exports.

{doc}`profiles`
:   The GenericSetup profiles this package ships, and what each one applies.
