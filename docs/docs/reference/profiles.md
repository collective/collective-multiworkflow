---
myst:
  html_meta:
    "description": "The GenericSetup profiles collective.multiworkflow ships, and what each one applies."
    "property=og:description": "The GenericSetup profiles collective.multiworkflow ships, and what each one applies."
    "property=og:title": "GenericSetup profiles"
    "keywords": "Plone, collective.multiworkflow, GenericSetup, profile, install"
---

(reference-profiles)=

# GenericSetup profiles

Four profiles, in two packages.
The two demo profiles exist only when the `collective.multiworkflow.demo` package's ZCML is loaded, which a plain installation does not do.

| Profile | Package | Applied by |
|---|---|---|
| `collective.multiworkflow:default` | `collective.multiworkflow` | installing the add-on |
| `collective.multiworkflow:uninstall` | `collective.multiworkflow` | uninstalling the add-on |
| `collective.multiworkflow.demo:demo` | `collective.multiworkflow.demo` | the integrator, explicitly |
| `collective.multiworkflow.demo:content` | `collective.multiworkflow.demo` | the integrator, explicitly |

## `collective.multiworkflow:default`

The installation profile.
Version `1000`; depends on `plone.volto:default`.

It applies the following.

- The `workflow_states` `KeywordIndex` and metadata column, described in {doc}`catalog`.
- The browser layer.
- A registry override making the **Review state** query field use the workflow states vocabulary.

It touches no content type and no workflow chain.
Installing this add-on changes nothing about a site's content until a behavior declares a contribution.

## `collective.multiworkflow:uninstall`

Removes the browser layer.
The profile is hidden from the add-ons control panel listing by a `HiddenProfiles` utility, as is conventional.

## `collective.multiworkflow.demo:demo`

The worked example.
Version `1000`; depends on `collective.multiworkflow:default`.

It applies the following.

- The `Profile` content type, carrying the `collective.multiworkflow.demo.foundation_member` behavior.
- The `foundation_member_workflow` workflow definition.
- A site-wide role map for the `collective.multiworkflow: Manage membership` permission, which the workflow then overrides per state.
- A `repositorytool` configuration for the new type.

Applying it is a plain GenericSetup import with no handler, so it stays inside the caller's transaction.

## `collective.multiworkflow.demo:content`

Example content showcasing the membership workflow.
Version `1000`; depends on `collective.multiworkflow.demo:demo`.

It runs a post-handler that imports example content.

The handler neither reindexes nor updates role mappings itself.
Keeping imported content correctly indexed and secured is handled for every importer at once, by the patch described in {doc}`api/exportimport`.

```{warning}
The importer behind this profile commits as it goes.
Do not apply it from an integration test layer, whose per-test rollback cannot undo those commits.
```

```{seealso}
{doc}`/how-to-guides/install-the-demo` for the steps that load the demo package and apply these two profiles.
```
