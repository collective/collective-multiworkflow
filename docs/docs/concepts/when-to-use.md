---
myst:
  html_meta:
    "description": "The kind of problem an additional workflow solves, three scenarios it fits, and the signs that a problem calls for something else."
    "property=og:description": "The kind of problem an additional workflow solves, three scenarios it fits, and the signs that a problem calls for something else."
    "property=og:title": "About when an additional workflow fits"
    "keywords": "Plone, collective.multiworkflow, use cases, membership, translation, records retention, workflow"
---

(concepts-when-to-use)=

# About when an additional workflow fits

An additional workflow is the right tool when content has a second lifecycle: a status that moves on its own, whether or not the content is published.
This page describes that kind of problem, walks through three scenarios that have it, and lists the signs that a problem calls for something else.

## The shape of the problem

Three questions decide whether a status belongs in an additional workflow.

**Does it change independently of publication?**
Publishing a page does not change it, and changing it neither publishes nor retracts the page.
If one always implies the other, the two are a single lifecycle, and a single workflow describes it better.

**Does it belong to some content and not the rest?**
An additional workflow arrives with a behavior, so it applies to the types that enable the behavior and to nothing else.
A status that every item in the site needs belongs in the publication workflow itself.

**Can its permissions stay apart from publication's?**
A workflow in a chain may manage permissions, but only permissions that no other workflow in the chain manages.
Plone's `simple_publication_workflow` manages `Access contents information`, `Modify portal content`, and `View`, so an additional workflow running alongside it must leave those three alone.
{doc}`permissions` explains why the rule admits no exception.

When all three answers are yes, the problem has the shape this package is built for.
The scenarios below show how the work divides between the two workflows.

## Membership lifecycle

A site for an association or a foundation holds a profile page for each member.

The publication workflow keeps deciding who can see the page: private while it is being written, published once it is ready.

The additional workflow owns the membership: `pending` while the application is considered, `active` once it is approved, `lapsed` when it expires, and `active` again on renewal.
A member whose membership lapses keeps a published page, and a page taken down for editing ends nobody's membership.

The worked example implements this scenario, and its workflow manages one permission of its own, `collective.multiworkflow: Manage membership`.
The pending state maps it to reviewers, and the active state to the page's owner.
The views and forms that change membership details should check that permission.
The workflow never manages `View`: whether a lapsed member's page stays visible is a publication decision, taken with a publication transition.

{doc}`/how-to-guides/install-the-demo` installs the worked example.

## Translation status

A multilingual site publishes each page in several languages, and each translation has to keep up with its original.

The publication workflow keeps deciding whether each translation is visible, exactly as it does for any page.

The additional workflow owns the translation's standing against its original: `untranslated`, `in_translation`, `translated`, and `outdated` once the original has changed since the translation was done.
A translation can be published and outdated at the same time, and that combination is the one translators most need to find.

This workflow needs no permission at all.
Its value is in its states: a catalog query on `workflow_states` lists every outdated translation for a translator's dashboard, and the Volto add-on shows each page's translation status beside its publication state.

Nothing in this package moves a translation to `outdated` when its original changes.
That takes an event subscriber of your own, on the event your site fires when the original is modified, built the way {doc}`/how-to-guides/react-to-another-workflow` builds one for a transition event.

## Records retention

An organization keeps documents as records, and some of them fall under a retention schedule or a legal hold.

The publication workflow keeps deciding who can see each document.

The additional workflow owns the record's retention status: `retained` while the schedule runs, `on_hold` while a legal hold applies, `eligible_for_disposal` once the schedule has ended with no hold in place, and `disposed`.
The hold is what makes a separate workflow necessary: placing a document on hold must not publish it, retract it, or change who can read it.

The permissions are where this scenario needs care.
The tempting design lets the hold state withdraw `Modify portal content`, so that nobody can edit a document on hold.
The publication workflow already manages that permission, so the two workflows would overwrite each other's mapping of it, and the next publication transition would restore edit rights on a document that is still on hold.

The workable design keeps the two apart.
The retention workflow manages a permission of its own, such as `my.package: Dispose of records`, which the disposal process checks.
Where a hold must also freeze publication, a guard on the publication workflow's transitions reads the retention state, as {doc}`/how-to-guides/react-to-another-workflow` shows.
A hold that must block editing outright is a restriction on `Modify portal content`, and among the workflows only the one managing that permission can impose it: the hold then belongs in the publication workflow's own states.

## When it does not fit

**The status is a step towards publication.**
An editorial review before a page goes live is part of the publication lifecycle.
Add the states to the publication workflow, where `review_state` already reports them.

**The workflow should depend on where content lives.**
A contribution depends on what the content is, never on its location.
{doc}`scope` explains why placeful workflows stay out of this package.

**Both workflows need the same permission.**
Two workflows managing one permission is a design error that this package reports and does not resolve.
Rework the permissions until the sets are disjoint, or merge the two lifecycles into one workflow.

**One status must always follow the other.**
If every transition in one workflow implies a transition in the other, they describe a single lifecycle.
An event subscriber can keep two workflows in step, but one workflow holding the combined states is easier to reason about.

```{seealso}
{doc}`workflow-chains` for what the package changes, and {doc}`/tutorials/add-a-second-workflow` to build the membership scenario from an empty add-on.
```
