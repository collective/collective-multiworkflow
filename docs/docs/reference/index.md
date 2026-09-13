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
compatibility
```

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} Python API
:link: api/index
:link-type: doc

Every public name in the Python package, generated from the source.
````

````{grid-item-card} ZCML directive
:link: zcml
:link-type: doc

The `<plone:additionalworkflows />` directive: its attributes, its validation, and the errors it raises.
````

````{grid-item-card} Catalog index
:link: catalog
:link-type: doc

The `workflow_states` index: the values it holds, the order it holds them in, and how `review_state` queries are rewritten onto it.
````

````{grid-item-card} REST API
:link: rest-api
:link-type: doc

The additions to the `@workflow` and `@history` endpoints, with generated request and response examples.
````

````{grid-item-card} Volto add-on
:link: volto
:link-type: doc

The components, helpers, actions, and types the Volto add-on exports.
````

````{grid-item-card} Profiles
:link: profiles
:link-type: doc

The GenericSetup profiles this package ships, and what each one applies.
````

````{grid-item-card} Compatibility
:link: compatibility
:link-type: doc

The release status, the Plone, Python, and Volto versions tested, Classic UI, and the changelogs.
````
`````
