---
myst:
  html_meta:
    "description": "Give a content type a second workflow that runs alongside publication, transition it, and find it in the catalog."
    "property=og:description": "Give a content type a second workflow that runs alongside publication, transition it, and find it in the catalog."
    "property=og:title": "Add a second workflow to a content type"
    "keywords": "Plone, collective.multiworkflow, tutorial, workflow, behavior, chain"
---

(tutorials-add-a-second-workflow)=

# Add a second workflow to a content type

In this tutorial we will give a content type a membership workflow that runs alongside its publication workflow.
We will transition an object through it, watch its publication state stay exactly where it was, and then find the object again with a catalog query.

By the end you will have written a workflow definition, a behavior marker, and a contribution declaration—the three pieces every additional workflow needs.

## What you need

- A Plone 6.2 site with `collective.multiworkflow` installed, as described in {doc}`/how-to-guides/install`.
- An add-on package of your own where we can put the new files.
  We will call it `my.package`.
- A way to run Python against the site: a debug shell, `plone.api` from a browser view, or a test.

## Step 1: Look at a chain before we change anything

Start a debug shell against your site and create a Document.

```python
from plone import api

portal = api.portal.get()
doc = api.content.create(
    container=portal, type="Document", title="A Document"
)
```

Now ask the workflow tool which workflows apply to it.

```python
wftool = api.portal.get_tool("portal_workflow")
wftool.getChainFor(doc)
```

You should see a chain of one.

```python
('simple_publication_workflow',)
```

Notice that this is a *tuple*, not a single workflow id.
Plone has always been able to answer with several—nothing here is being unlocked, only used.

## Step 2: Write the workflow definition

In your package, create `profiles/default/workflows/membership_workflow/definition.xml`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<dc-workflow
    workflow_id="membership_workflow"
    title="Membership"
    state_variable="workflow_states"
    initial_state="pending"
    >

  <state state_id="pending" title="Pending">
    <exit-transition transition_id="membership_activate" />
  </state>

  <state state_id="active" title="Active">
    <exit-transition transition_id="membership_lapse" />
  </state>

  <state state_id="lapsed" title="Lapsed">
    <exit-transition transition_id="membership_activate" />
  </state>

  <transition transition_id="membership_activate"
              title="Activate membership"
              new_state="active"
              trigger="USER"
              action="Activate membership"
              />

  <transition transition_id="membership_lapse"
              title="Lapse membership"
              new_state="lapsed"
              trigger="USER"
              action="Lapse membership"
              />

</dc-workflow>
```

Two details in there are the whole point of this file.

`state_variable` is `workflow_states`, not `review_state`.
This workflow will record its own state under its own name, so the publication workflow keeps `review_state` to itself.

The transition ids are prefixed with `membership_`.
Transition ids have to be unique across every workflow in a chain, and a plain `activate` is much likelier to collide with something one day.

Register the workflow in `profiles/default/workflows.xml`.

```xml
<?xml version="1.0" encoding="utf-8"?>
<object name="portal_workflow">
  <object name="membership_workflow" meta_type="Workflow" />
</object>
```

## Step 3: Declare the marker and the contribution

Create the marker interface in `interfaces.py`.

```python
from collective.multiworkflow.interfaces import IAdditionalWorkflows


class IMember(IAdditionalWorkflows):
    """Marker for content whose membership status is tracked."""
```

Extending `IAdditionalWorkflows` is what makes this marker participate.
The chain adapter is registered for that base interface, so anything extending it is picked up with no further wiring.

Now register the behavior and the contribution in `configure.zcml`.

```xml
<configure
    xmlns:plone="http://namespaces.plone.org/plone"
    i18n_domain="my.package"
    >

  <plone:behavior
      name="my.package.member"
      title="Member"
      description="Track a membership lifecycle alongside publication."
      provides=".interfaces.IMember"
      />

  <plone:additionalworkflows
      marker=".interfaces.IMember"
      workflows="membership_workflow"
      label="Membership status"
      />

</configure>
```

That second directive is the declaration this whole package is built around: *content providing this marker also runs this workflow.*

Its `label` is optional.
It is the name the REST API and the Volto interface show for the workflow, in place of the workflow's title, and it is translated in the `i18n_domain` of this file.
Without it, the workflow is shown under its own title, `Membership`.

Restart your instance so the new ZCML is read, and reapply your package's profile so the workflow is installed.

## Step 4: Enable the behavior and look again

Enable **Member** on the Document type, in the types control panel or in your FTI.

Now create a *new* Document and ask for its chain again.

```python
doc = api.content.create(
    container=portal, type="Document", title="A Member Document"
)
wftool.getChainFor(doc)
```

This time you should see two workflows.

```python
('simple_publication_workflow', 'membership_workflow')
```

Notice the order.
The workflow your content type was configured with comes first, and yours was appended after it.
That ordering is guaranteed, and the rest of the package relies on it.

## Step 5: Transition the membership workflow

Read both states at once.

```python
from collective.multiworkflow import api as mw_api

mw_api.get_states(doc)
```

```python
{'simple_publication_workflow': 'private', 'membership_workflow': 'pending'}
```

Now activate the membership.

```python
mw_api.transition(
    doc, "membership_activate", workflow_id="membership_workflow"
)
mw_api.get_states(doc)
```

```python
{'simple_publication_workflow': 'private', 'membership_workflow': 'active'}
```

Look carefully at what did *not* happen.
The membership state moved from `pending` to `active`, and `review_state` is still `private`.

Confirm that with the call any Plone code would make.

```python
api.content.get_state(doc)
```

```python
'private'
```

That is the guarantee at the heart of this package: `review_state` means what it has always meant, no matter how many workflows you add.

## Step 6: Find the document by its membership state

Every workflow in the chain is indexed.
Build the value with `format_state` and query for it.

```python
from collective.multiworkflow.utils.workflow import format_state

results = api.content.find(
    workflow_states=format_state("membership_workflow", "active")
)
[brain.Title for brain in results]
```

```python
['A Member Document']
```

Now ask for something more interesting: published documents whose membership is active.

```python
results = api.content.find(
    workflow_states={
        "query": [
            format_state("simple_publication_workflow", "published"),
            format_state("membership_workflow", "active"),
        ],
        "operator": "and",
    }
)
[brain.Title for brain in results]
```

```python
[]
```

Empty—our document is still private.
Publish it and run the same query again.

```python
api.content.transition(doc, "publish")
results = api.content.find(
    workflow_states={
        "query": [
            format_state("simple_publication_workflow", "published"),
            format_state("membership_workflow", "active"),
        ],
        "operator": "and",
    }
)
[brain.Title for brain in results]
```

```python
['A Member Document']
```

Two workflows, one query, one index.

## What you have built

You gave a content type a second workflow, drove it independently of publication, and searched across both.

Along the way you used the three things every additional workflow needs.

- A **workflow definition** with its own `state_variable` and collision-proof transition ids.
- A **marker interface** extending `IAdditionalWorkflows`.
- A **contribution declaration** tying the two together.

## Where to go next

- {doc}`/concepts/workflow-chains` explains what was actually happening under each of those steps.
- {doc}`/how-to-guides/write-a-composing-workflow` covers the fourth constraint we did not need here: what to do when your workflow manages permissions.
- {doc}`/reference/rest-api` shows how the chain reaches a REST client and the Volto interface.
