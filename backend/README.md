<div align="center">

<h1 align="center">Multi-Workflow Support for Plone</h1>
<h2 align="center">collective.multiworkflow</h2>

</div>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)
[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/collective-multiworkflow)](https://github.com/collective/collective-multiworkflow)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/collective-multiworkflow?style=social)](https://github.com/collective/collective-multiworkflow)

[![CI](https://github.com/collective/collective-multiworkflow/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective-multiworkflow/actions/workflows/main.yml)

</div>

The backend package for Multi-Workflow Support for Plone — a Plone 6 add-on that assigns additional workflows to content types through behaviors, and carries them through the catalog, the REST API, and Volto.
See also the frontend package [@plone-collective/volto-multiworkflow](https://www.npmjs.com/package/@plone-collective/volto-multiworkflow).

## Features

When a content type provides a participating behavior, this package **appends** one or more additional workflows to that type's workflow chain. The type's configured chain is never replaced, and content that does not provide the behavior is left completely untouched.

- **Behavior-driven chains** — a behavior marker interface extends `IAdditionalWorkflows` and declares the workflow ids it contributes with one ZCML directive. A workflow chain adapter, registered for that marker, appends them to the type's existing chain.

  ```xml
  <configure xmlns:plone="http://namespaces.plone.org/plone">
    <plone:additionalworkflows
        marker=".interfaces.IFoundationMember"
        workflows="foundation_member_workflow"
        />
  </configure>
  ```

  `workflows` is a whitespace-separated list, appended in the order given. A `marker` that does not extend `IAdditionalWorkflows` raises `ConfigurationError` while the ZCML is read, rather than being ignored at runtime. The directive is available as soon as this package is installed — `Products.CMFPlone` auto-includes add-on `meta.zcml` — but a package that wants to be explicit can `<include package="collective.multiworkflow" file="meta.zcml" />` first. For contributions ZCML cannot express, the `contributes()` factory the directive wraps stays public.
- **Deterministic composition** — the base chain order is preserved, contributed workflows are appended in interface resolution order, and duplicates are removed. A contributed workflow id that does not exist in `portal_workflow` is logged and skipped rather than breaking chain lookup.
- **`review_state` is never affected** — each additional workflow uses its own `state_variable`, so Plone's publication workflow behaves exactly as before.
- **Workflow-aware helpers** — `get_state`, `get_states`, `transition`, and `transitions` read and drive per-workflow state. Their defaults reproduce today's `plone.api` behavior exactly. `conflicting_permissions` audits a chain for workflows claiming the same permission.
- **REST API** — on participating content, the `@workflow` endpoint gains a `chain` key with one entry per workflow (`workflow_id`, `title`, `state`, `state_variable`, `transitions`, `history`), and its top-level `transitions` list is narrowed to the primary workflow, so a client written before this package cannot present an unrelated workflow's transitions as publication actions. `@history` merges every chain workflow's transitions into the single time-sorted stream it already returns, tagging every entry with a `workflow_id` (`null` for versioning entries). Both are registered on the marker interface, so content that provides no participating behavior is served core's payload untouched — with no `chain` key at all, which is what a client should test for.
- **Catalog support** — the installation profile adds one `workflow_states` `KeywordIndex` describing an object's whole chain, so a site gains no further indexes as behaviors contribute more workflows. Values read `<workflow-id>|<state-id>` and are in chain order; build them with `format_state()` and read them back with `parse_state()`. Parsed `review_state` collection queries are rewritten onto it, so collections written before the add-on keep working.
- **Import-safe** — `plone.exportimport` restores workflow state by assigning `workflow_history` directly, which fires no transition and so leaves an additional workflow's catalog entry stale. `collective.multiworkflow.exportimport` patches the importer to reindex what it changed. The patch is generic, names no index of this package's own, and is written to be moved upstream.
- **Fully typed** — every public API is annotated, `mypy` runs over the package in CI, and a PEP 561 `py.typed` marker ships in the wheel, so consumers type check against this package rather than around it.

### Requirements for additional workflows

An additional workflow may manage permissions. `DCWorkflowDefinition` rewrites only the permissions listed in its own `permissions`, and executing a transition re-applies the mappings of the transitioning workflow alone, so workflows sharing a chain compose as long as their permission sets do not overlap.

- Declare `workflow_states` as the `state_variable`; never `review_state`.
  Using the same name as the catalog index is what makes `WorkflowTool._reindexWorkflowVariables` keep that index fresh on every transition, with no subscriber involved. Sharing the name across workflows is safe, because DCWorkflow keys its status records by workflow id rather than by variable name. A workflow keeping a bespoke variable still works: an event handler reindexes for it, but only when nothing else will.
- Keep transition ids unique across every workflow in a type's chain.
- Keep managed permissions disjoint across the chain. Where two workflows claim the same permission, the mapping is left as whichever transitioned last wrote it, and stays that way until the other transitions or `portal_workflow.updateRoleMappings()` runs. `conflicting_permissions(obj)` reports the overlap for a given object.

### Not in scope

- Placeful workflows (`CMFPlacefulWorkflow`) integration.
- Sub-workflows — a transition in one workflow triggering another. The chain model is concurrent, not hierarchical.
- Reconciling workflows that manage the *same* permission — the package reports the conflict rather than arbitrating it.
- Any change to `review_state` semantics.

### Trying the example

The package ships an example — a `foundation_member` behavior and a `foundation_member_workflow` that tracks a membership lifecycle — but installing `collective.multiworkflow` deliberately does **not** add a behavior to your site.
The example lives in the `collective.multiworkflow.demo` subpackage, which the root `configure.zcml` never includes, so neither the behavior nor its `demo` profile exists in a plain installation.

To see it running, load that package's ZCML explicitly and apply its profile.
This repository's `instance.yaml` already does the first part for local development:

```yaml
zcml_package_includes: 'collective.multiworkflow,collective.multiworkflow.demo'
```

then install the `collective.multiworkflow.demo:demo` profile. `make create-site` does both.

## Documentation

Full documentation is published at [collective.github.io/collective-multiworkflow](https://collective.github.io/collective-multiworkflow/), and its source lives in [`docs/`](https://github.com/collective/collective-multiworkflow/tree/main/docs) at the repository root.

The pages closest to this package are the [Python API reference](https://github.com/collective/collective-multiworkflow/blob/main/docs/docs/reference/api/index.md), the [ZCML directive](https://github.com/collective/collective-multiworkflow/blob/main/docs/docs/reference/zcml.md), the [catalog index](https://github.com/collective/collective-multiworkflow/blob/main/docs/docs/reference/catalog.md), and the [REST API](https://github.com/collective/collective-multiworkflow/blob/main/docs/docs/reference/rest-api.md), whose request and response examples are generated by this package's own test suite, in `tests/docs/`.

## Installation

Install collective.multiworkflow with uv.

```shell
uv add collective.multiworkflow
```

Create the Plone site.

```shell
make create-site
```

## Contribute

- [Issue tracker](https://github.com/collective/collective-multiworkflow/issues)
- [Source code](https://github.com/collective/collective-multiworkflow/)

### Prerequisites ✅

-   An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
-   [uv](https://6.docs.plone.org/install/create-project-cookieplone.html#uv)
-   [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
-   [Docker](https://docs.docker.com/get-started/get-docker/) (optional)

### Installation 🔧

1.  Clone this repository.

    ```shell
    git clone git@github.com:collective/collective-multiworkflow.git
    cd collective-multiworkflow/backend
    ```

2.  Install this code base.

    ```shell
    make install
    ```


### Add features using `plonecli` or `bobtemplates.plone`

This package provides markers as strings (`<!-- extra stuff goes here -->`) that are compatible with [`plonecli`](https://github.com/plone/plonecli) and [`bobtemplates.plone`](https://github.com/plone/bobtemplates.plone).
These markers act as hooks to add all kinds of features through subtemplates, including behaviors, control panels, upgrade steps, or other subtemplates from `bobtemplates.plone`.
`plonecli` is a command line client for `bobtemplates.plone`, adding autocompletion and other features.

To add a feature as a subtemplate to your package, use the following command pattern.

```shell
make add <template_name>
```

For example, you can add a content type to your package with the following command.

```shell
make add content_type
```

You can add a behavior with the following command.

```shell
make add behavior
```

```{seealso}
You can check the list of available subtemplates in the [`bobtemplates.plone` `README.md` file](https://github.com/plone/bobtemplates.plone/?tab=readme-ov-file#provided-subtemplates).
See also the documentation of [Mockup and Patternslib](https://6.docs.plone.org/classic-ui/mockup.html) for how to build the UI toolkit for Classic UI.
```

## License

The project is licensed under GPLv2.

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0b3)](https://github.com/plone/cookieplone) and [cookieplone-templates (61a8f90)](https://github.com/plone/cookieplone-templates/commit/61a8f90e5408ce0a5337e3fdf6723369a4864ee8) on 2026-08-07 16:01:41.322560. A special thanks to all contributors and supporters!
