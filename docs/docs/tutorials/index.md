---
myst:
  html_meta:
    "description": "Learn collective.multiworkflow by giving a content type a second workflow and driving it end to end."
    "property=og:description": "Learn collective.multiworkflow by giving a content type a second workflow and driving it end to end."
    "property=og:title": "Tutorials"
    "keywords": "Plone, collective.multiworkflow, tutorial, learning, workflow"
---

(tutorials-index)=

# Tutorials

This part of the documentation teaches the package by building something with it.
Follow a tutorial from start to finish; every step produces a result you can see.

```{toctree}
:maxdepth: 1
:hidden: true

add-a-second-workflow
manage-workflows-in-volto
```

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} Add a second workflow to a content type
:link: add-a-second-workflow
:link-type: doc

Give a content type a membership workflow that runs alongside publication, transition it without disturbing `review_state`, and find the content again with a catalog query.
+++
Start here.
````

````{grid-item-card} Manage additional workflows in Volto
:link: manage-workflows-in-volto
:link-type: doc

Drive that second workflow from the Volto interface, and read a history that spans both workflows.
````
`````

```{seealso}
The Diátaxis framework calls this class of documentation [tutorials](https://diataxis.fr/tutorials/).
```
