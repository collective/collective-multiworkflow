<div align="center">

<h1 align="center">Multi-Workflow Support for Plone</h1>

</div>

<div align="center">

[![Built with Cookieplone](https://img.shields.io/badge/built%20with-Cookieplone-0083be.svg?logo=cookiecutter)](https://github.com/plone/cookieplone-templates/)


[![PyPI](https://img.shields.io/pypi/v/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)
[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/collective.multiworkflow)](https://pypi.org/project/collective.multiworkflow/)


[![npm](https://img.shields.io/npm/v/@plone-collective/volto-multiworkflow)](https://www.npmjs.com/package/@plone-collective/volto-multiworkflow)
[![Storybook](https://img.shields.io/badge/-Storybook-ff4785?logo=Storybook&logoColor=white&style=flat-square)](https://collective.github.io/collective-multiworkflow/storybook/)


[![GitHub contributors](https://img.shields.io/github/contributors/collective/collective-multiworkflow)](https://github.com/collective/collective-multiworkflow)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/collective-multiworkflow?style=social)](https://github.com/collective/collective-multiworkflow)

[![CI](https://github.com/collective/collective-multiworkflow/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective-multiworkflow/actions/workflows/main.yml)

</div>

Assign additional workflows to content types through behaviors, with full support in plone.restapi and Volto.

## What it does 📋

Plone's `portal_workflow` has always supported *chains* — more than one workflow active on the same content type at the same time. This package makes that capability practical and behavior-driven.

When a content type provides a participating behavior, this add-on **appends** one or more extra workflows to that type's workflow chain. The type's configured chain is never replaced, and content that does not provide the behavior is left completely untouched.

- **Behavior-driven** — enable a behavior on a type, and its extra workflows come along. No manual `portal_workflow` chain editing per type.
- **`review_state` is never affected** — each additional workflow uses its own `state_variable`, so Plone's publication workflow keeps working exactly as before.
- **Workflow-aware helpers** — read and transition per-workflow state with `plone.api`-style functions, whose defaults behave identically to today's API.
- **REST API** — on participating content, the `@workflow` endpoint gains a `chain` key describing every workflow in the chain (state, state variable, available transitions, history), and its top-level `transitions` list is narrowed to the primary workflow so a client written before this package cannot show an unrelated workflow's transitions as publication actions.
  `@history` reports every workflow's transitions in one stream, each entry tagged with its `workflow_id` (`null` for versioning entries). Existing keys keep their values, and content that provides no participating behavior is served exactly the payload Plone has always served, with no `chain` key at all.
- **Volto** — the workflow control shows one selector per additional workflow alongside the publication one, and the history view attributes every entry to the workflow that recorded it. Both render exactly as upstream on content without additional workflows.
- **Searchable** — one `workflow_states` catalog index describes an object's whole chain, so additional states can be queried like any other index and a site gains no further indexes as behaviors contribute more workflows.
  Existing `review_state` collection criteria are rewritten onto it and keep working.
- **Import-safe** — `plone.exportimport` restores workflow state by writing it directly rather than by transitioning, which leaves an additional workflow's catalog entry stale. This package patches the importer so imported content is indexed correctly; the patch is written for upstreaming.
- **Ships no behavior of its own** — the worked example lives in the `collective.multiworkflow.demo` subpackage, which is not loaded by default.
  Installing the add-on changes nothing about your content types until you declare a behavior.

### Supported configuration

An additional workflow may manage permissions — a common reason to add one is precisely to control access the publication workflow does not. Each workflow rewrites only the permissions it declares, and a transition re-applies the mappings of the transitioning workflow alone, so the requirement is that the permission sets be **disjoint**:

- Each additional workflow must declare its own `state_variable`, never `review_state`. Declare `workflow_states`, the same name as the catalog index: `WorkflowTool._reindexWorkflowVariables` then keeps that index fresh on every transition at no cost. Sharing the name across workflows is safe, because DCWorkflow keys its status records by workflow id.
- Transition ids must be unique across every workflow in a type's chain.
- No two workflows in a chain may manage the same permission. Where they do, the mapping is left as whichever workflow transitioned last wrote it, until the other transitions or `portal_workflow.updateRoleMappings()` runs.
  `api.conflicting_permissions(obj)` reports any such overlap.

### Not in scope

- Placeful workflows (`CMFPlacefulWorkflow`) integration.
- Sub-workflows — a transition in one workflow triggering another. The chain model is concurrent, not hierarchical.
- Reconciling workflows that manage the *same* permission — this package reports the conflict rather than arbitrating it.
- Any change to `review_state` semantics.

## Documentation 📚

Full documentation lives in [`docs/`](./docs) and is published at [collective.github.io/collective-multiworkflow](https://collective.github.io/collective-multiworkflow/).

- **Start here:** [Add a second workflow to a content type](./docs/docs/tutorials/add-a-second-workflow.md) — build one end to end.
- **How-to guides:** [installing](./docs/docs/how-to-guides/install.md), [declaring a contribution](./docs/docs/how-to-guides/declare-additional-workflows.md), [writing a workflow that composes](./docs/docs/how-to-guides/write-a-composing-workflow.md), [searching by state](./docs/docs/how-to-guides/search-by-workflow-state.md).
- **Concepts:** [chains](./docs/docs/concepts/workflow-chains.md), [state variables](./docs/docs/concepts/state-variables.md), [permissions](./docs/docs/concepts/permissions.md).
- **Reference:** [Python API](./docs/docs/reference/api/index.md), [ZCML directive](./docs/docs/reference/zcml.md), [catalog index](./docs/docs/reference/catalog.md), [REST API](./docs/docs/reference/rest-api.md), [Volto add-on](./docs/docs/reference/volto.md).

## Install in your project 🔧

Both packages are installed separately. The backend one is enough on its own; the frontend one requires it.

### Backend

Requires Plone 6.2 and Python 3.11 or later.

```shell
uv add collective.multiworkflow
```

Then install **Multi-Workflow Support for Plone** from the add-ons control panel.

### Frontend

Requires Volto 18 and above.

Add `@plone-collective/volto-multiworkflow` to your `package.json`.

```json
"addons": [
    "@plone-collective/volto-multiworkflow"
],
"dependencies": {
    "@plone-collective/volto-multiworkflow": "*"
}
```

> [!IMPORTANT]
> Adding the package to `dependencies` without listing it under `addons` installs the code but never registers it, so nothing is rendered.

## Quick Start 🏁

### Prerequisites ✅

-   An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
-   [uv](https://6.docs.plone.org/install/create-project-cookieplone.html#uv)
-   [nvm](https://6.docs.plone.org/install/create-project-cookieplone.html#nvm)
-   [Node.js and pnpm](https://6.docs.plone.org/install/create-project.html#node-js) 24
-   [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
-   [Docker](https://docs.docker.com/get-started/get-docker/) (optional)


### Installation 🔧

1.  Clone this repository, then change your working directory.

    ```shell
    git clone git@github.com:collective/collective-multiworkflow.git
    cd collective-multiworkflow
    ```

2.  Install this code base.

    ```shell
    make install
    ```


### Fire Up the Servers 🔥

1.  Create a new Plone site on your first run.

    ```shell
    make backend-create-site
    ```

2.  Start the backend at http://localhost:8080/.

    ```shell
    make backend-start
    ```

3.  In a new shell session, start the frontend at http://localhost:3000/.

    ```shell
    make frontend-start
    ```

Voila! Your Plone site should be live and kicking! 🎉

### Local Stack Deployment 📦

Deploy a local Docker Compose environment that includes the following.

- Docker images for Backend and Frontend 🖼️
- A stack with a Traefik router and a PostgreSQL database 🗃️
- Accessible at [http://collective-multiworkflow.localhost](http://collective-multiworkflow.localhost) 🌐

Run the following commands in a shell session.

```shell
make stack-create-site
make stack-start
```

And... you're all set! Your Plone site is up and running locally! 🚀

## Project structure 🏗️

This monorepo consists of the following distinct sections:

- **backend**: The Plone add-on `collective.multiworkflow`, installed with uv, plus its test suite.
- **frontend**: The Volto add-on `@plone-collective/volto-multiworkflow`, plus its Storybook stories.
- **docs**: The Sphinx documentation published at [collective.github.io/collective-multiworkflow](https://collective.github.io/collective-multiworkflow/).

### Why this structure? 🤔

- Both halves of the add-on live together, so a change to the REST API payload and the change to the component that reads it are one commit.
- GitHub Workflows are triggered per section, so a documentation change does not rebuild the frontend (refer to .github/workflows).
- The documentation can generate its API reference from the backend source and its REST examples from the backend test suite, because both are in the same checkout.

## Code quality assurance 🧐

To check your code against quality standards, run the following shell command.

```shell
make check
```

### Format the codebase

To format and rewrite the code base, ensuring it adheres to quality standards, run the following shell command.

```shell
make format
```

| Section | Tool | Description | Configuration |
| --- | --- | --- | --- |
| backend | Ruff | Python code formatting, imports sorting  | [`backend/pyproject.toml`](./backend/pyproject.toml) |
| backend | `zpretty` | XML and ZCML formatting  | -- |
| frontend | ESLint | Fixes most common frontend issues | [`frontend/.eslintrc.js`](./frontend/.eslintrc.js) |
| frontend | prettier | Format JS and Typescript code  | [`frontend/.prettierrc`](./frontend/.prettierrc) |
| frontend | Stylelint | Format Styles (css, less, sass)  | [`frontend/.stylelintrc`](./frontend/.stylelintrc) |

Formatters can also be run within the `backend` or `frontend` folders.

### Linting the codebase
or `lint`:

 ```shell
make lint
```

| Section | Tool | Description | Configuration |
| --- | --- | --- | --- |
| backend | Ruff | Checks code formatting, imports sorting  | [`backend/pyproject.toml`](./backend/pyproject.toml) |
| backend | Pyroma | Checks Python package metadata  | -- |
| backend | check-python-versions | Checks Python version information  | -- |
| backend | `zpretty` | Checks XML and ZCML formatting  | -- |
| frontend | ESLint | Checks JS / Typescript lint | [`frontend/.eslintrc.js`](./frontend/.eslintrc.js) |
| frontend | prettier | Check JS / Typescript formatting  | [`frontend/.prettierrc`](./frontend/.prettierrc) |
| frontend | Stylelint | Check Styles (css, less, sass) formatting  | [`frontend/.stylelintrc`](./frontend/.stylelintrc) |

Linters can be run individually within the `backend` or `frontend` folders.

## Internationalization 🌐

Generate translation files for Plone and Volto with ease:

```shell
make i18n
```

## Packages 📦

This repository holds two packages, released separately and each under its own license.

| Package | Location | Registry | License |
| ------- | -------- | -------- | ------- |
| `collective.multiworkflow` | [backend/](./backend/) | [PyPI](https://pypi.org/project/collective.multiworkflow/) | GPL-2.0-only |
| `@plone-collective/volto-multiworkflow` | [frontend/](./frontend/) | [npm](https://www.npmjs.com/package/@plone-collective/volto-multiworkflow) | MIT |

The backend package is usable on its own: it needs no frontend to append workflows, index their states, or serve them over the REST API. The frontend package requires the backend, because everything it renders comes from the `chain` key that backend adds to the `@workflow` payload.

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0b3)](https://github.com/plone/cookieplone) and [cookieplone-templates (61a8f90)](https://github.com/plone/cookieplone-templates/commit/61a8f90e5408ce0a5337e3fdf6723369a4864ee8) on 2026-08-07 16:01:41.322560. A special thanks to all contributors and supporters!
