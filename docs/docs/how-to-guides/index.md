---
myst:
  html_meta:
    "description": "Directions for installing collective.multiworkflow, declaring additional workflows, and searching by their states."
    "property=og:description": "Directions for installing collective.multiworkflow, declaring additional workflows, and searching by their states."
    "property=og:title": "How-to guides"
    "keywords": "Plone, collective.multiworkflow, how-to, guides, install, workflow"
---

(howto-index)=

# How-to guides

This part of the documentation contains directions toward a result.
Each guide assumes you already know what you want and shows you how to get it.

If you are meeting the package for the first time, work through {doc}`/tutorials/add-a-second-workflow` instead.

```{toctree}
:maxdepth: 1
:hidden: true

install
install-the-demo
declare-additional-workflows
write-a-composing-workflow
read-and-transition-state
search-by-workflow-state
audit-permission-conflicts
consume-the-rest-api
customize-the-volto-components
add-to-an-existing-site
```

## Getting set up

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} Install the package
:link: install
:link-type: doc

Add the backend package and the Volto add-on to a project, and install the profile.
````

````{grid-item-card} Install the worked example
:link: install-the-demo
:link-type: doc

Load the worked example and see an additional workflow running end to end.
````

````{grid-item-card} Add to an existing site
:link: add-to-an-existing-site
:link-type: doc

Populate the new catalog index on a site that already holds content.
````
`````

## Declaring workflows

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} Declare additional workflows
:link: declare-additional-workflows
:link-type: doc

Make a behavior contribute workflows to every type that enables it.
````

````{grid-item-card} Write a composing workflow
:link: write-a-composing-workflow
:link-type: doc

Write a workflow definition that composes with the one already in the chain.
````
`````

## Working with the states

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} Read and transition state
:link: read-and-transition-state
:link-type: doc

Read a specific workflow's state, and execute a transition belonging to it.
````

````{grid-item-card} Search by workflow state
:link: search-by-workflow-state
:link-type: doc

Find content by its state in any workflow, from code and from a collection.
````

````{grid-item-card} Audit permission conflicts
:link: audit-permission-conflicts
:link-type: doc

Find permissions claimed by more than one workflow, and resolve the overlap.
````
`````

## Building an interface

`````{grid} 1 1 2 2
:gutter: 3

````{grid-item-card} Consume the REST API
:link: consume-the-rest-api
:link-type: doc

Read the chain, execute a transition, and read the merged history from a REST client.
````

````{grid-item-card} Customize the Volto components
:link: customize-the-volto-components
:link-type: doc

Restyle the controls, read the chain in a component of your own, and shadow what the add-on ships.
````
`````

```{seealso}
The Diátaxis framework calls this class of documentation [how-to guides](https://diataxis.fr/how-to-guides/).
```
