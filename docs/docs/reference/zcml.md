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

`label`
:   Optional. The name the user interface shows for the workflow, in place of its title.
    It is translatable: the text is a message id in the `i18n_domain` of the ZCML file declaring it.
    Only valid when `workflows` names exactly one workflow.

```xml
<configure
    xmlns:plone="http://namespaces.plone.org/plone"
    i18n_domain="my.package"
    >

  <plone:additionalworkflows
      marker=".interfaces.IFoundationMember"
      workflows="foundation_member_workflow"
      label="Foundation membership"
      />

</configure>
```

### What it registers

One subscription adapter on `marker`, providing `IAdditionalWorkflowsFor` and returning the given ids.

A subscription adapter, rather than a plain one, is what makes an object providing several participating markers collect the contributions of all of them.

With `label`, the directive also registers one utility providing `IAdditionalWorkflowLabel`, named after the workflow id, whose component is the label.
The label belongs to the workflow rather than to the marker, so it names the workflow wherever it appears.
The `@workflow` endpoint reports it, translated, as the chain entry's `title`, and the vocabulary of the **Review state** collection criterion names the workflow's states with it.
A workflow with no declared label keeps its own title in both places.

(reference-zcml-order)=

### Order of contributions

Within one directive, the workflows are appended in the order `workflows` lists them.

When several participating behaviors contribute to the same object, their workflows are appended in the reverse of the order the behaviors are listed in the content type's `behaviors`: the behavior listed last contributes first.
The order in which the directives are read plays no part.

```xml
<property name="behaviors">
  <element value="my.package.member" />
  <element value="my.package.peer_reviewed" />
</property>
```

With `my.package.member` contributing `membership_workflow` and `my.package.peer_reviewed` contributing `peer_review_workflow`, the chain of a `Document` reads as follows.

```python
('simple_publication_workflow', 'peer_review_workflow', 'membership_workflow')
```

A marker applied to an object with `alsoProvides` follows the same rule: markers given later contribute first.

The order is a consequence of how contributions are collected, not a policy of this package.
`plone.dexterity` provides an object's behavior markers in the order the type lists them, and `zope.component` returns the subscribers of an object's interfaces starting from the least specific one.
The test suite asserts it, in `backend/tests/chain/test_contribution_order.py`.

### Errors

The directive raises `ConfigurationError` while the configuration is being read in the following cases.

- `marker` does not extend `IAdditionalWorkflows`.
  Such a marker would leave the chain adapter inapplicable, and the contribution would be ignored at runtime with nothing to show for it.
  Failing at configuration time instead is the point of the check.
- `label` is given while `workflows` names more or fewer than one workflow.
  Nothing would say which workflow the label names.
  Declare each labelled workflow in a directive of its own.

Two directives labelling the same workflow raise `ConfigurationConflictError`, as any two utilities registered under one name do.
Declare a workflow's label once, even when several markers contribute that workflow.

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

To label the workflow as well, register the label as a utility named after the workflow id.

```python
from collective.multiworkflow.interfaces import IAdditionalWorkflowLabel
from zope.i18nmessageid import MessageFactory

_ = MessageFactory("my.package")
getGlobalSiteManager().registerUtility(
    _("Foundation membership"),
    IAdditionalWorkflowLabel,
    name="foundation_member_workflow",
)
```

The directive is the same registration in one line, and it validates the marker and the label.
Prefer it.

```{seealso}
{doc}`/how-to-guides/declare-additional-workflows` for the surrounding steps.
```
