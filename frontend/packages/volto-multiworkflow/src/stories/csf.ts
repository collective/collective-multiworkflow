/**
 * Minimal Component Story Format types.
 *
 * `@storybook/react` is not a dependency of this package and is not resolvable
 * from it — Storybook runs from the Volto workspace, which supplies the
 * runtime. Declaring the two shapes we use keeps the stories type checked
 * against their components' props without adding a dependency that only the
 * workspace would ever satisfy.
 */

import type { ComponentType, ReactElement } from 'react';

export interface StoryMeta<P> {
  /** Path in Storybook's sidebar. */
  title: string;
  component: ComponentType<P>;
  args?: Partial<P>;
  argTypes?: Record<string, unknown>;
  parameters?: Record<string, unknown>;
  decorators?: Array<(Story: ComponentType) => ReactElement>;
}

export interface Story<P> {
  name?: string;
  args?: Partial<P>;
  parameters?: Record<string, unknown>;
  decorators?: Array<(Story: ComponentType) => ReactElement>;
  render?: (args: P) => ReactElement;
}
