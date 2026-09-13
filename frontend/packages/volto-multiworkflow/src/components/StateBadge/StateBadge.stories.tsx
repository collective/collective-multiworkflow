/**
 * `StateBadge` renders one workflow's current state, for listings.
 */

import StateBadge from './StateBadge';
import type { StateBadgeProps } from './StateBadge';
import { getAdditionalWorkflowStates } from '../../helpers/states';
import {
  contentWithWorkflowStates,
  labelledMembership,
  membership,
  publication,
  review,
  workflowStateTitles,
} from '../../stories/fixtures';
import type { Story, StoryMeta } from '../../stories/csf';

const meta: StoryMeta<StateBadgeProps> = {
  title: 'Multiworkflow/StateBadge',
  component: StateBadge,
  parameters: {
    docs: {
      description: {
        component:
          'A compact label for one workflow state, rendered from a chain entry ' +
          'or from a `workflow_states` value. Titles arrive translated from ' +
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

/**
 * A workflow whose directive declares a label.
 *
 * The backend reports the label as the entry's `title`, so the badge names the
 * workflow by it with no change of its own. Hover to see it.
 */
export const DeclaredLabel: Story<StateBadgeProps> = {
  args: { entry: labelledMembership },
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

/**
 * From a `workflow_states` value, labelled from the workflow states vocabulary.
 *
 * Content and catalog summaries carry these values, so a listing renders them
 * with no `@workflow` request per item.
 */
export const FromValue: Story<StateBadgeProps> = {
  args: {
    value: 'foundation_member_workflow|active',
    label: 'Membership: Active',
  },
};

/** A value with no label: the badge falls back to the state id. */
export const FromValueWithoutLabel: Story<StateBadgeProps> = {
  args: { value: 'foundation_member_workflow|active' },
};

/** A listing item's additional states, read from its `workflow_states`. */
export const InAListingFromValues: Story<StateBadgeProps> = {
  render: () => (
    <div style={{ display: 'flex', gap: '0.5rem' }}>
      {getAdditionalWorkflowStates(contentWithWorkflowStates).map((value) => (
        <StateBadge
          key={value}
          value={value}
          label={workflowStateTitles[value]}
        />
      ))}
    </div>
  ),
};
