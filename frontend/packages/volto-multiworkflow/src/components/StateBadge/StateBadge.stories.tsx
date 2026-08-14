/**
 * `StateBadge` renders one workflow's current state, for listings.
 */

import StateBadge from './StateBadge';
import type { StateBadgeProps } from './StateBadge';
import { membership, publication, review } from '../../stories/fixtures';
import type { Story, StoryMeta } from '../../stories/csf';

const meta: StoryMeta<StateBadgeProps> = {
  title: 'Multiworkflow/StateBadge',
  component: StateBadge,
  parameters: {
    docs: {
      description: {
        component:
          'A compact label for one chain entry. Titles arrive translated from ' +
          'the backend, so the component does no i18n of its own. Style it ' +
          'through the `data-workflow` and `data-state` attributes, which ' +
          'carry stable ids rather than translated text.',
      },
    },
  },
};

export default meta;

/** An additional workflow's state — the case this add-on exists for. */
export const Additional: Story<StateBadgeProps> = {
  args: { entry: membership },
};

/** The badge works just as well for the publication workflow. */
export const Publication: Story<StateBadgeProps> = {
  args: { entry: publication },
};

/** A longer state title, to check the label does not get truncated. */
export const LongStateTitle: Story<StateBadgeProps> = {
  args: { entry: review },
};

/** Extra class names are appended, so a theme can restyle the badge. */
export const CustomClassName: Story<StateBadgeProps> = {
  args: { entry: membership, className: 'my-theme-badge' },
};

/** Several badges together, which is how a listing shows them. */
export const InAListing: Story<StateBadgeProps> = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.5rem' }}>
      <StateBadge entry={publication} />
      <StateBadge entry={membership} />
      <StateBadge entry={review} />
    </div>
  ),
};
