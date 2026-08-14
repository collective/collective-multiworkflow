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
add-to-an-existing-site
```

## Getting set up

{doc}`install`
:   Add the backend package and the Volto add-on to a project, and install the profile.

{doc}`install-the-demo`
:   Load the worked example and see an additional workflow running end to end.

{doc}`add-to-an-existing-site`
:   Populate the new catalog index on a site that already holds content.

## Declaring workflows

{doc}`declare-additional-workflows`
:   Make a behavior contribute workflows to every type that enables it.

{doc}`write-a-composing-workflow`
:   Write a workflow definition that composes with the one already in the chain.

## Working with the states

{doc}`read-and-transition-state`
:   Read a specific workflow's state, and execute a transition belonging to it.

{doc}`search-by-workflow-state`
:   Find content by its state in any workflow, from code and from a collection.

{doc}`audit-permission-conflicts`
:   Find permissions claimed by more than one workflow, and resolve the overlap.

```{seealso}
The Diátaxis framework calls this class of documentation [how-to guides](https://diataxis.fr/how-to-guides/).
```
