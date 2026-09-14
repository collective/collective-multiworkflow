---
myst:
  html_meta:
    "description": "Allow a transition only while another workflow is in a given state, or transition one workflow when another one transitions."
    "property=og:description": "Allow a transition only while another workflow is in a given state, or transition one workflow when another one transitions."
    "property=og:title": "How to make one workflow react to another"
    "keywords": "Plone, collective.multiworkflow, guard, guard expression, event subscriber, IAfterTransitionEvent, workflow"
---

(howto-react-to-another-workflow)=

# How to make one workflow react to another

This guide shows you two ways to make a workflow in a chain depend on another one: a guard that allows a transition only while another workflow is in a given state, and an event subscriber that transitions one workflow when another one transitions.

This package couples no workflow to another.
The workflows in a chain are peers, so a dependency between two of them is something you add, in your own workflow definition or your own code, where it stays visible.
{doc}`/concepts/scope` explains why the package leaves it to you.

## Prerequisites

- An additional workflow of your own, declared as described in {doc}`declare-additional-workflows`.
- The examples use the worked example's membership workflow alongside `simple_publication_workflow`.
  {doc}`install-the-demo` installs it.

```{note}
The worked example's transition ids, such as `activate`, predate the advice in {doc}`write-a-composing-workflow` to prefix them.
Prefix the ids in workflows of your own.
```

## Allow a transition only in a given state of another workflow

A guard expression on the transition reads the state of the other workflow.
This `activate` transition, in the membership workflow's `definition.xml`, can be executed only while the content is published.

```xml
<transition after_script=""
            before_script=""
            new_state="active"
            title="Activate membership"
            transition_id="activate"
            trigger="USER"
>
  <description>Approve or renew the membership.</description>
  <action category="workflow"
          icon=""
          url="%(content_url)s/content_status_modify?workflow_action=activate"
  >Activate</action>
  <guard>
    <guard-permission>Modify portal content</guard-permission>
    <guard-expression>python: here.portal_workflow.getInfoFor(here, 'review_state', wf_id='simple_publication_workflow') == 'published'</guard-expression>
  </guard>
</transition>
```

The expression runs with `here` bound to the content object.
`portal_workflow.getInfoFor` reads a workflow variable, and its `wf_id` argument names the workflow to read it from.
Read `review_state` from the publication workflow, and `workflow_states` from an additional workflow that declares it as its state variable.

Import the workflow definition again, as for any other change to `definition.xml`.
From then on, while the content is not published, `activate` is unavailable, and executing it with `mw_api.transition` raises `InvalidParameterError`.

The dependency can run in the other direction too.
In a publication workflow of your own, this guard expression on `publish` allows only content whose membership is active to be published.

```text
python: here.portal_workflow.getInfoFor(here, 'workflow_states', wf_id='foundation_member_workflow') == 'active'
```

```{warning}
Do not use `collective.multiworkflow.api` in a guard expression.
Guard expressions run as restricted Python, which refuses to import it: an expression reaching the module through `modules['collective.multiworkflow.api']` raises `Unauthorized` when the guard is checked.
`portal_workflow.getInfoFor` is public to restricted code, which is why the expressions above use it.
```

A guard decides whether a transition can happen at the moment it is attempted, and has no effect after that.
Once the membership is active, retracting the content leaves the membership `active`.

## Transition another workflow when a transition happens

An event subscriber can move one workflow when another one transitions.
This one, in a `subscribers.py` module, activates the membership of content as soon as the content is published.

```python
from collective.multiworkflow import api as mw_api


def activate_membership_on_publish(obj, event):
    """Activate the membership of content as soon as it is published."""
    if event.workflow.getId() != "simple_publication_workflow":
        return
    if event.new_state.getId() != "published":
        return
    if mw_api.get_state(obj, workflow_id="foundation_member_workflow") != "pending":
        return
    mw_api.transition(obj, "activate", workflow_id="foundation_member_workflow")
```

Register it for the behavior's marker and `IAfterTransitionEvent`, in the `configure.zcml` next to `subscribers.py`.

```xml
<configure xmlns="http://namespaces.zope.org/zope">

  <subscriber
      for="collective.multiworkflow.demo.behavior.IFoundationMember
           Products.DCWorkflow.interfaces.IAfterTransitionEvent"
      handler=".subscribers.activate_membership_on_publish"
      />

</configure>
```

Restart the instance.
ZCML is read at start-up, so the subscriber is registered only after a restart.

DCWorkflow fires `IAfterTransitionEvent` after a transition of any of its workflows, carrying the workflow in `event.workflow` and the state reached in `event.new_state`.
The subscriber checks both first, so that it acts on publication and ignores every other transition, including the membership workflow's own.

It then checks the membership's current state.
From a state that `activate` does not leave, `mw_api.transition` raises `InvalidParameterError`, and the error propagates out of the publication transition that fired the event.
With the check in place, publishing content whose membership is already active, or has lapsed, leaves the membership as it is.

```{seealso}
{doc}`read-and-transition-state` for the helpers the subscriber uses, and {doc}`/concepts/when-to-use` for when two statuses are better kept as one workflow.
```
