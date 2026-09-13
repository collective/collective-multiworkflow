---
myst:
  html_meta:
    "description": "Make a behavior contribute one or more workflows to the chain of every content type that enables it."
    "property=og:description": "Make a behavior contribute one or more workflows to the chain of every content type that enables it."
    "property=og:title": "How to declare additional workflows for a behavior"
    "keywords": "Plone, collective.multiworkflow, behavior, ZCML, marker interface"
---

(howto-declare-additional-workflows)=

# How to declare additional workflows for a behavior

This guide shows you how to make a behavior contribute one or more workflows to the chain of every content type that enables it.

## Prerequisites

- An add-on package with its own `configure.zcml`.
- A workflow to contribute, installed by a GenericSetup profile.
  To write one that composes safely, see {doc}`write-a-composing-workflow`.

## 1. Define the marker interface

Your behavior's marker interface must extend `IAdditionalWorkflows`.

```python
from collective.multiworkflow.interfaces import IAdditionalWorkflows


class IFoundationMember(IAdditionalWorkflows):
    """Marker for content whose membership status is tracked."""
```

That base marker is the single registration point for the chain adapter.
A marker that does not extend it never reaches the adapter, and the declaration in step 3 refuses to configure.

## 2. Register the behavior

Register the marker as a behavior in the usual way.

```xml
<configure xmlns:plone="http://namespaces.plone.org/plone">

  <plone:behavior
      name="my.package.foundation_member"
      title="Foundation member"
      description="Track a membership lifecycle alongside publication."
      provides=".interfaces.IFoundationMember"
      />

</configure>
```

No factory is needed.
With none, `plone.behavior` applies the interface to content as a marker, which is all the mechanism requires.

## 3. Declare the contribution

```xml
<plone:additionalworkflows
    marker=".interfaces.IFoundationMember"
    workflows="foundation_member_workflow"
    />
```

To contribute several workflows, separate their ids with whitespace.
They are appended in the order given, after the workflows the content type is already configured with.

To show the workflow under a name other than its title, give it a `label`.

```xml
<plone:additionalworkflows
    marker=".interfaces.IFoundationMember"
    workflows="foundation_member_workflow"
    label="Foundation membership"
    />
```

The label is translated in the `i18n_domain` of your ZCML file, so add it to your package's message catalogs like any other string.
A directive with a `label` must name exactly one workflow; declare each labelled workflow in a directive of its own.

See {doc}`/reference/zcml` for the directive's full description.

## 4. Enable the behavior on a type

Enable it as you would any behavior, in the type's FTI.

```xml
<property name="behaviors">
  <element value="my.package.foundation_member" />
</property>
```

Every object of that type now resolves a chain with your workflow appended.

## Register from Python instead

Use `contributes` where ZCML cannot express the declaration—building a contribution from configuration read at start-up, for instance.

```python
from collective.multiworkflow.declaration import contributes
from collective.multiworkflow.interfaces import IAdditionalWorkflowsFor
from zope.component import getGlobalSiteManager

factory = contributes(IFoundationMember, "foundation_member_workflow")
getGlobalSiteManager().registerSubscriptionAdapter(
    factory, (IFoundationMember,), IAdditionalWorkflowsFor
)
```

Register it as a **subscription** adapter, as shown.
A plain adapter has one winner per interface, so content providing two participating behaviors would gain the workflows of only one of them.

## Verify

Create an object of the type and read its chain.

```python
from plone import api

wftool = api.portal.get_tool("portal_workflow")
chain = wftool.getChainFor(obj)

assert chain == (
    "simple_publication_workflow",
    "foundation_member_workflow",
)
```

If your workflow is missing from the chain, check the instance log.
A contributed id that no workflow answers to is logged and skipped, so that a bad declaration cannot break chain lookup and make the object unusable.

```{seealso}
{doc}`/concepts/behavior-driven-assignment` for why the mechanism is built this way.
```
