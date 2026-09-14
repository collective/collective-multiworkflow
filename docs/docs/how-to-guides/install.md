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

This guide shows you how to add the package to an existing Plone 6.2 project, backend and frontend.

Installing it changes nothing about your content types.
It adds one catalog index and waits for a behavior to declare a contribution.

## Prerequisites

- A Plone 6.2 project with a backend and, if you use it, a Volto frontend.
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

Add the package to the dependencies of your frontend.

```shell
cd frontend
pnpm add @plone-collective/volto-multiworkflow
```

Then register it in `frontend/volto.config.js`, so Volto loads its configuration and its component shadows.

```js
const addons = ["@plone-collective/volto-multiworkflow"];
const theme = "";

module.exports = {
  addons,
  theme,
};
```

```{important}
Adding the dependency is not enough on its own.
An add-on that is installed but not listed in `addons` contributes nothing: its reducer is never registered, and its shadows are never resolved.
```

The add-on shadows Volto's `Workflow` and `History` components.
Both shadows render exactly as upstream on content that has no additional workflows, so adding the add-on before you declare any behavior is safe.

## 3. Install the add-on in your site

Declare the profile as a dependency of your policy package's own profile, in `profiles/default/metadata.xml`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<metadata>
  <version>1000</version>
  <dependencies>
    <dependency>profile-collective.multiworkflow:default</dependency>
  </dependencies>
</metadata>
```

Installing your policy package now installs this one with it, on every site you create, in the right order and with no manual step to forget.

If you have no policy package, install **Multi-Workflow Support for Plone** from the {menuselection}`Site Setup --> Add-ons` control panel instead.

Either route applies the `workflow_states` catalog index and the browser layer.
See {doc}`/reference/profiles` for everything the profile touches.

## 4. Verify the installation

Check that the catalog now has the index.

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
