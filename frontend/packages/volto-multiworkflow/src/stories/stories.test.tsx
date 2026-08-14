/**
 * Every story renders.
 *
 * A Storybook *build* only indexes stories; it never runs them, so a story
 * that throws still produces a green build and a broken page. This test walks
 * every story module, renders each export the way Storybook would — meta args
 * merged with story args, decorators applied outside in — and fails on the
 * first one that cannot mount.
 *
 * It is deliberately shallow about *what* is rendered. The point is that the
 * fixtures still satisfy the components' props, which is exactly what rots when
 * a payload shape changes.
 */

import { describe, expect, it } from 'vitest';
import { render } from '@testing-library/react';
import { IntlProvider } from 'react-intl';
import { StaticRouter } from 'react-router-dom';
import type { ComponentType, ReactElement } from 'react';

import * as additionalWorkflow from '../components/AdditionalWorkflow/AdditionalWorkflow.stories';
import * as additionalWorkflowMenu from '../components/AdditionalWorkflowMenu/AdditionalWorkflowMenu.stories';
import * as historyTable from '../components/History/HistoryTable.stories';
import * as optionLabel from '../components/Workflow/OptionLabel.stories';
import * as stateBadge from '../components/StateBadge/StateBadge.stories';
import * as stateDot from '../components/Workflow/StateDot.stories';

/** The shape the story modules export, loosely typed for iteration. */
interface StoryModule {
  default: {
    component: ComponentType<Record<string, unknown>>;
    args?: Record<string, unknown>;
    decorators?: Array<(Story: ComponentType) => ReactElement>;
  };
  [name: string]: unknown;
}

interface StoryExport {
  args?: Record<string, unknown>;
  decorators?: Array<(Story: ComponentType) => ReactElement>;
  render?: (args: Record<string, unknown>) => ReactElement;
}

const modules: Array<[string, StoryModule]> = [
  ['AdditionalWorkflow', additionalWorkflow as unknown as StoryModule],
  ['AdditionalWorkflowMenu', additionalWorkflowMenu as unknown as StoryModule],
  ['HistoryTable', historyTable as unknown as StoryModule],
  ['OptionLabel', optionLabel as unknown as StoryModule],
  ['StateBadge', stateBadge as unknown as StoryModule],
  ['StateDot', stateDot as unknown as StoryModule],
];

/** Wrap in the providers `.storybook/preview.jsx` supplies to every story. */
function withPreviewProviders(node: ReactElement): ReactElement {
  return (
    <IntlProvider messages={{}} locale="en" defaultLocale="en">
      <StaticRouter location="/">{node}</StaticRouter>
    </IntlProvider>
  );
}

/**
 * Build the element Storybook would render for one story.
 *
 * Decorators are applied story-first then meta, which is the order Storybook
 * uses — the meta's decorator ends up outermost.
 */
function renderStory(
  meta: StoryModule['default'],
  story: StoryExport,
): ReactElement {
  const args = { ...meta.args, ...story.args };
  const Component = meta.component;

  let element: ReactElement = story.render ? (
    story.render(args)
  ) : (
    <Component {...args} />
  );

  const decorators = [...(story.decorators ?? []), ...(meta.decorators ?? [])];
  for (const decorator of decorators) {
    // Capture the element by value. Closing over the loop variable instead
    // makes the wrapper return whatever `element` holds *at render time* —
    // which is the decorator's own output — and React recurses until the heap
    // gives out.
    const child = element;
    const Current = () => child;
    element = decorator(Current);
  }

  return withPreviewProviders(element);
}

describe.each(modules)('%s stories', (_name, module) => {
  const meta = module.default;
  const stories = Object.entries(module).filter(
    ([name]) => name !== 'default',
  ) as Array<[string, StoryExport]>;

  it('exports at least one story', () => {
    expect(stories.length).toBeGreaterThan(0);
  });

  it.each(stories)('%s renders', (_storyName, story) => {
    expect(() => render(renderStory(meta, story))).not.toThrow();
  });
});
