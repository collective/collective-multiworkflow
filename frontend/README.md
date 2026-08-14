<div align="center">

<h1 align="center">Multi-Workflow Support for Plone</h1>
<h2 align="center">@plone-collective/volto-multiworkflow</h2>

</div>

<div align="center">

[![npm](https://img.shields.io/npm/v/@plone-collective/volto-multiworkflow)](https://www.npmjs.com/package/@plone-collective/volto-multiworkflow)
[![](https://img.shields.io/badge/-Storybook-ff4785?logo=Storybook&logoColor=white&style=flat-square)](https://collective.github.io/collective-multiworkflow/storybook/)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/collective-multiworkflow)](https://github.com/collective/collective-multiworkflow)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/collective-multiworkflow?style=social)](https://github.com/collective/collective-multiworkflow)

[![CI](https://github.com/collective/collective-multiworkflow/actions/workflows/main.yml/badge.svg)](https://github.com/collective/collective-multiworkflow/actions/workflows/main.yml)

</div>

Assign additional workflows to content types through behaviors, with full support in plone.restapi and Volto.

## Features

The frontend package for Multi-Workflow Support for Plone — a Plone 6 add-on that assigns additional workflows to content types through behaviors, and carries them through the catalog, the REST API, and Volto. See also the backend package [collective.multiworkflow](https://pypi.org/project/collective.multiworkflow/).

This package surfaces the additional workflows a content object participates in, alongside Plone's regular publication workflow. It requires the backend package to be installed on the Plone site.

Once installed, the workflow control in the toolbar renders one state selector per workflow in the object's chain, the publication workflow included, and the history view attributes every entry to the workflow that recorded it. Nothing else needs wiring.

- **Shadowed `Workflow`** — the existing control gains one selector per additional workflow, rather than a separate menu entry, so all of an object's states are read and changed in one place.
- **Shadowed `History`** — a merged history breaks the assumption that the preceding entry is the previous state, because it usually belongs to another workflow. This view threads each workflow through its own states, and names the workflow on every row once a history spans more than one.
- **`AdditionalWorkflowMenu`** — shows one additional workflow's current state and the transitions available to the user, and executes them.
- **`StateBadge`** — renders an additional workflow's state in listings.
- **Payload-driven** — everything renders from the `chain` key of the `@workflow` endpoint's response. That key is absent on content with no additional workflows, in which case both shadowed components render exactly what upstream Volto renders.
- **Typed contract** — the `WorkflowChainEntry`, `WorkflowState`, `WorkflowTransition`, `WorkflowInfo`, and `HistoryEntry` interfaces are exported and mirror the REST API payload, so consumers get the contract for free.
- **No dependency on any specific behavior** — the add-on works with whatever additional workflows the backend exposes.

### Using the components directly

The add-on registers its own Redux reducer, because Volto's built-in workflow reducer keeps only the state, history, and transitions of the effective workflow and discards the rest of the response.

```jsx
import {
  AdditionalWorkflowMenu,
  StateBadge,
  getAdditionalWorkflows,
} from '@plone-collective/volto-multiworkflow';
```

`AdditionalWorkflowMenu` is presentational: give it the `chain` array and an `onTransition` callback. `AdditionalWorkflow` is the store-connected wrapper, and takes the content object's `url`.

A transition's response is the last `review_history` entry rather than a workflow payload, so the chain has to be re-fetched afterwards. The connected wrapper already does this; a component driving `transitionMultiWorkflow` directly has to.

Titles arrive already translated from the backend, so the components need no i18n of their own. Style them through the `data-workflow` and `data-state` attributes, which carry stable ids rather than translated text.

## Documentation

Full documentation is published at [collective.github.io/collective-multiworkflow](https://collective.github.io/collective-multiworkflow/), and its source lives in [`docs/`](https://github.com/collective/collective-multiworkflow/tree/main/docs) at the repository root.

The pages closest to this package are the [Volto add-on reference](https://github.com/collective/collective-multiworkflow/blob/main/docs/docs/reference/volto.md), which lists every export, and the [REST API reference](https://github.com/collective/collective-multiworkflow/blob/main/docs/docs/reference/rest-api.md), which describes the payloads these components render.

## Installation

This add-on supports Volto 18 and above.

To install this add-on on your project, add `@plone-collective/volto-multiworkflow` to your `package.json`.

```json
"addons": [
    "@plone-collective/volto-multiworkflow"
],
"dependencies": {
    "@plone-collective/volto-multiworkflow": "*"
}
```

## Test installation

Visit http://localhost:3000/ in a browser, login, and check the awesome new features.


## Development

The development of this add-on is done in isolation using pnpm workspaces, the latest `mrs-developer`, and other Volto core improvements.
For these reasons, development requires pnpm and Volto 18 or above. `mrs.developer.json` pins the version this repository develops against.


### Prerequisites ✅

-   An [operating system](https://6.docs.plone.org/install/create-project-cookieplone.html#prerequisites-for-installation) that runs all the requirements mentioned.
-   [nvm](https://6.docs.plone.org/install/create-project-cookieplone.html#nvm)
-   [Node.js and pnpm](https://6.docs.plone.org/install/create-project.html#node-js) 24
-   [Make](https://6.docs.plone.org/install/create-project-cookieplone.html#make)
-   [Git](https://6.docs.plone.org/install/create-project-cookieplone.html#git)
-   [Docker](https://docs.docker.com/get-started/get-docker/) (optional)

### Installation 🔧

1.  Clone this repository, then change your working directory.

    ```shell
    git clone git@github.com:collective/collective-multiworkflow.git
    cd collective-multiworkflow/frontend
    ```

2.  Install this code base.

    ```shell
    make install
    ```


### Make convenience commands

Run `make help` to list the available Make commands.


### Set up development environment

Install package requirements.

```shell
make install
```

### Start developing

Start the backend.

```shell
make backend-docker-start
```

In a separate terminal session, start the frontend.

```shell
make start
```

### Lint code

Run ESlint, Prettier, and Stylelint in analyze mode.

```shell
make lint
```

### Format code

Run ESlint, Prettier, and Stylelint in fix mode.

```shell
make format
```

### i18n

Extract the i18n messages to locales.

```shell
make i18n
```

### Unit tests

Run unit tests.

```shell
make test
```

### Storybook

Every component this add-on ships has stories, and they are the fastest way to see one without a running Plone site.

Start Storybook on [port 6006](http://localhost:6006/).

```shell
make storybook-start
```

Build the static site, as CI does before publishing it:

```shell
make storybook-build
```

#### Writing a story

Stories live next to their component, as `<Component>.stories.tsx`, and use Component Story Format 3. Payloads come from `src/stories/fixtures.ts`, which holds chains and histories shaped exactly like the backend serves them — reuse those rather than inventing a payload, so a story that renders is evidence the component handles the real contract.

```tsx
import StateBadge from './StateBadge';
import type { StateBadgeProps } from './StateBadge';
import { membership } from '../../stories/fixtures';
import type { Story, StoryMeta } from '../../stories/csf';

const meta: StoryMeta<StateBadgeProps> = {
  title: 'Multiworkflow/StateBadge',
  component: StateBadge,
};

export default meta;

export const Additional: Story<StateBadgeProps> = {
  args: { entry: membership },
};
```

Two conventions are worth knowing before you write one.

- **The types come from `src/stories/csf.ts`, not from `@storybook/react`.**
  Storybook runs from the Volto workspace and supplies the runtime, but the package itself does not depend on it, so `@storybook/react` is not resolvable here. The local `StoryMeta` and `Story` types keep `args` checked against the component's props without a dependency only the workspace could satisfy.
- **A component that needs the store gets one from `src/stories/withStore.tsx`.**
  Volto's `FormattedDate` reads `state.intl.locale`, for instance. The decorator supplies a static store whose `dispatch` does nothing, so a story cannot navigate away from the state its fixture describes.

```tsx
decorators: [withStore({ multiworkflow: { loading: false, loaded: true, error: null, chain } })],
```

A component that reaches for react-select is a different matter: Volto loads that library lazily through `injectLazyLibs`, and it is not resolvable from this package either. Rather than stub it, the visual pieces of the workflow control were split out — `StateDot` and `OptionLabel` render standalone and carry the stories, while the react-select decorators stay thin glue. Prefer that shape over stubbing a library.

#### Stories are tested

A Storybook build only *indexes* stories; it never renders them, so a story that throws still produces a green build. `src/stories/stories.test.tsx` renders every story the way Storybook would — meta args merged with story args, decorators applied outside in — and `make test` runs it. A new story is covered automatically once it is exported.

### Run Cypress tests

Run each of these steps in separate terminal sessions.

In the first session, start the frontend in development mode.

```shell
make acceptance-frontend-dev-start
```

In the second session, start the backend acceptance server.

```shell
make acceptance-backend-start
```

In the third session, start the Cypress interactive test runner.

```shell
make acceptance-test
```

## License

The project is licensed under the MIT license.


## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0b3)](https://github.com/plone/cookieplone) and [cookieplone-templates (61a8f90)](https://github.com/plone/cookieplone-templates/commit/61a8f90e5408ce0a5337e3fdf6723369a4864ee8) on 2026-08-07 16:01:41.322560. A special thanks to all contributors and supporters!
