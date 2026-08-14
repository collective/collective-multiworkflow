---
myst:
  html_meta:
    "description": "The plone:additionalworkflows ZCML directive, its attributes, and the errors it raises."
    "property=og:description": "The plone:additionalworkflows ZCML directive, its attributes, and the errors it raises."
    "property=og:title": "ZCML directive"
    "keywords": "Plone, collective.multiworkflow, ZCML, directive, behavior"
---

(reference-zcml)=

# ZCML directive

## `<plone:additionalworkflows />`

Declares the workflows a behavior marker contributes to the chain of every content object providing it.

```xml
<configure xmlns:plone="http://namespaces.plone.org/plone">

  <plone:additionalworkflows
      marker=".interfaces.IFoundationMember"
      workflows="foundation_member_workflow"
      />

</configure>
```

The directive is in the `http://namespaces.plone.org/plone` namespace.
It is available as soon as this package's `meta.zcml` is loaded, which happens automatically in a Plone site through the `plone.autoinclude.plugin` entry point.
A test layer with autoinclude switched off must load it explicitly.

### Attributes

`marker`
:   **Required.** The behavior's marker interface, as a dotted name.
    It must extend `collective.multiworkflow.interfaces.IAdditionalWorkflows`.

`workflows`
:   **Required.** Whitespace-separated ids of the workflows this marker contributes, in order.
    They are appended after the workflows the content type is already configured with, never in place of them.

### What it registers

One subscription adapter on `marker`, providing `IAdditionalWorkflowsFor` and returning the given ids.

A subscription adapter, rather than a plain one, is what makes an object providing several participating markers collect the contributions of all of them.

### Errors

The directive raises `ConfigurationError` while the configuration is being read if `marker` does not extend `IAdditionalWorkflows`.

Such a marker would leave the chain adapter inapplicable, and the contribution would be ignored at runtime with nothing to show for it.
Failing at configuration time instead is the point of the check.

### Equivalent Python registration

Use `collective.multiworkflow.declaration.contributes` for the cases ZCML cannot express, such as a contribution built from configuration read at start-up.

```python
from collective.multiworkflow.declaration import contributes
from collective.multiworkflow.interfaces import IAdditionalWorkflowsFor
from zope.component import getGlobalSiteManager

factory = contributes(IFoundationMember, "foundation_member_workflow")
getGlobalSiteManager().registerSubscriptionAdapter(
    factory, (IFoundationMember,), IAdditionalWorkflowsFor
)
```

The directive is the same registration in one line, and it validates the marker.
Prefer it.

```{seealso}
{doc}`/how-to-guides/declare-additional-workflows` for the surrounding steps.
```
