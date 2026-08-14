---
myst:
  html_meta:
    "description": "Restyle the additional workflow controls, read the chain in your own Volto component, and shadow the components this add-on ships."
    "property=og:description": "Restyle the additional workflow controls, read the chain in your own Volto component, and shadow the components this add-on ships."
    "property=og:title": "How to customize the Volto components"
    "keywords": "Plone, collective.multiworkflow, Volto, React, shadowing, customization"
---

(howto-customize-the-frontend-components)=

# How to customize the Volto components

This guide shows you how to change what `@plone-collective/volto-multiworkflow` renders, and how to use its pieces in components of your own.

Work through the options in order.
Styling solves most requirements without any JavaScript, and shadowing a component is the last resort rather than the first move.

## Prerequisites

- A Volto project with the add-on registered in `volto.config.js`, as described in {doc}`install`.
- Content participating in at least one additional workflow, so there is something to render.

## Restyle the toolbar control

In the toolbar, each workflow gets its own select control, wrapped in a field whose class names the workflow.

`.field-wrapper-state-select`
:   The publication workflow, as upstream has always wrapped it.

`.field-wrapper-state-select-<workflow_id>`
:   One per additional workflow, for example `.field-wrapper-state-select-foundation_member_workflow`.

Target an individual workflow through that class.

```scss
.field-wrapper-state-select-foundation_member_workflow .react-select__control {
  border-color: var(--color-accent);
}
```

The controls use `react-select` with the `react-select` class prefix, so the usual `react-select__control`, `react-select__menu`, and `react-select__option` hooks are available under each id.

## Restyle a state badge

`StateBadge` carries the workflow id and the state id as data attributes.

```html
<span class="multiworkflow-state-badge" data-workflow="foundation_member_workflow" data-state="active">
  Active
</span>
```

Key your CSS on those attributes rather than on the visible text.

```scss
.multiworkflow-state-badge[data-state='active'] {
  background: var(--color-success);
}

.multiworkflow-state-badge[data-state='lapsed'] {
  background: var(--color-warning);
}
```

```{important}
Never key styling or acceptance tests on the rendered title.
Titles are translated by the backend serializer before they reach the browser, so they change with the user's language while the ids do not.
```

## Show a state badge in your own component

`StateBadge` renders one chain entry and takes no store connection, so you can drop it anywhere you already hold a chain entry.

```tsx
import { StateBadge, getAdditionalWorkflows } from '@plone-collective/volto-multiworkflow';

function MembershipColumn({ chain }) {
  return (
    <>
      {getAdditionalWorkflows(chain).map((entry) => (
        <StateBadge key={entry.workflow_id} entry={entry} className="my-badge" />
      ))}
    </>
  );
}
```

## Read the chain in your own component

The add-on installs a reducer under `multiworkflow`, because Volto's own workflow reducer keeps only `state`, `history`, and `transitions` from the response and drops `chain`.

Dispatch `getMultiWorkflow` for the object you care about, then read the chain from that reducer.

```tsx
import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  getMultiWorkflow,
  hasAdditionalWorkflows,
} from '@plone-collective/volto-multiworkflow';

function MembershipNotice({ url }) {
  const dispatch = useDispatch();
  const chain = useSelector((state) => state.multiworkflow?.chain ?? []);

  useEffect(() => {
    dispatch(getMultiWorkflow(url));
  }, [dispatch, url]);

  if (!hasAdditionalWorkflows(chain)) {
    return null;
  }

  return <MembershipColumn chain={chain} />;
}
```

Content without additional workflows reduces to an empty `chain`, so returning `null` on `hasAdditionalWorkflows` is all the guarding you need.

```{important}
Re-fetch after a transition.
The transition endpoint answers with a single history entry rather than a workflow payload, so the new state can only be learned by asking `@workflow` again.
`AdditionalWorkflow` already does this; a component of your own must do it too.
```

## Shadow a component this add-on ships

Volto's customization mechanism works on add-on packages, not only on Volto itself.
Mirror the path the file has inside the add-on's `src`, under a folder named for the package.

```text
src/customizations/@plone-collective/volto-multiworkflow/components/StateBadge/StateBadge.tsx
```

The resolver swaps `jsx` for `tsx` and `js` for `ts`, so either extension shadows the other.

Re-export the original when you only want to wrap it.

```tsx
import Original from '@plone-collective/volto-multiworkflow/components/StateBadge/StateBadge';

export default function StateBadge(props) {
  return <Original {...props} className="my-badge" />;
}
```

```{note}
An add-on can be customized only when it is registered, either in `package.json`'s `addons` key or in the `paths` of `tsconfig.json`.
Registering it in `volto.config.js` is what makes this true for a project.
```

## Replace the whole workflow control

The add-on shadows two of Volto's own components.

`volto/components/manage/Workflow/Workflow`
:   Renders one selector per workflow in the chain, publication included, in a single control.

`volto/components/manage/History/History`
:   Renders the merged history, naming the workflow of each entry when the history spans more than one.

If you shadow either of these in your project, your version wins over the add-on's, and the add-on's rendering is gone entirely.
Build on the add-on's exports rather than starting from the upstream component, or you lose the chain handling along with it.

```{warning}
A project shadow of `Workflow` replaces the add-on's, not just Volto's.
Additional workflows disappear from the interface with no error, because a component that never reads `chain` renders exactly as it did before the add-on was installed.
```

## Keep a shadow current across a Volto upgrade

Both files the add-on shadows are kept deliberately close to upstream, with their changes confined to blocks marked `--- collective.multiworkflow ---`.

Upgrading Volto is therefore a small, repeatable job.

1. Copy the new upstream component over the shadow.
2. Re-apply the marked blocks.
3. Run the frontend test suite.

Apply the same discipline to shadows of your own.
Keeping the diff against upstream small is what makes the next upgrade cheap.

```{seealso}
{doc}`/reference/volto` lists every component, helper, action, and type the add-on exports.

{doc}`consume-the-rest-api` covers the payload these components read, for a client that is not Volto.
```
