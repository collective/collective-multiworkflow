---
myst:
  html_meta:
    "description": "Add the backend package and the Volto add-on to a Plone project, then install the profile."
    "property=og:description": "Add the backend package and the Volto add-on to a Plone project, then install the profile."
    "property=og:title": "How to install collective.multiworkflow"
    "keywords": "Plone, collective.multiworkflow, install, add-on, Volto"
---

(howto-install)=

# How to install `collective.multiworkflow`

This guide shows you how to add the package to an existing Plone 6 project, backend and frontend.

Installing it changes nothing about your content types.
It adds one catalog index and waits for a behavior to declare a contribution.

## Prerequisites

- A Plone 6 project with a backend and, if you use it, a Volto frontend.
- Python 3.11 or later.

## 1. Add the backend package

Add `collective.multiworkflow` to your policy package's dependencies.

```toml
dependencies = [
    "Products.CMFPlone",
    "collective.multiworkflow",
]
```

Then install it as your project normally does.

```shell
make backend-install
```

The package declares a `plone.autoinclude.plugin` entry point, so its ZCML—including the `meta.zcml` that provides the directive—is loaded automatically in a Plone site.
You do not need a `<include />` for it.

## 2. Add the Volto add-on

Add `@plone-collective/volto-multiworkflow` to your frontend and register it in `volto.config.js`.

```js
const addons = ["@plone-collective/volto-multiworkflow"];

module.exports = {
  addons,
};
```

Then install the frontend dependencies.

```shell
make frontend-install
```

The add-on shadows Volto's `Workflow` and `History` components.
Both shadows render exactly as upstream on content that has no additional workflows, so adding the add-on before you declare any behavior is safe.

## 3. Install the add-on in your site

Install **Multi-Workflow Support for Plone** from the add-ons control panel, or apply its profile from a setup handler.

```python
from plone import api

setup_tool = api.portal.get_tool("portal_setup")
setup_tool.runAllImportStepsFromProfile("profile-collective.multiworkflow:default")
```

This applies the `workflow_states` catalog index and the browser layer.
See {doc}`/reference/profiles` for everything the profile touches.

## 4. Verify the installation

Query the new index.
An empty result is the expected answer at this point, and it confirms the index exists.

```python
from plone import api

catalog = api.portal.get_tool("portal_catalog")
assert "workflow_states" in catalog.indexes()
```

## Next steps

- To see the mechanism working before writing anything, install the worked example: {doc}`install-the-demo`.
- To give your own behavior a workflow, continue with {doc}`declare-additional-workflows`.

```{note}
On an existing site with content, reindex after installing so the new index is populated.
See {doc}`add-to-an-existing-site`.
```
