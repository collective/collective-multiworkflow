/**
 * `StateDot` is the coloured marker in the workflow select.
 */

import StateDot from './StateDot';
import type { StateDotProps } from './StateDot';
import type { Story, StoryMeta } from '../../stories/csf';

const meta: StoryMeta<StateDotProps> = {
  title: 'Multiworkflow/Workflow/StateDot',
  component: StateDot,
  args: { color: '#007bc1' },
  parameters: {
    docs: {
      description: {
        component:
          'Filled for the state an object is currently in, outlined for the ' +
          'others. The colours come from Volto’s workflow helpers, which ' +
          'map them from the state id.',
      },
    },
  },
};

export default meta;

/** The current state. */
export const Filled: Story<StateDotProps> = {
  args: { outlined: false },
};

/** Any other option in the menu. */
export const Outlined: Story<StateDotProps> = {
  args: { outlined: true },
};

/** The palette Plone's publication workflow uses, side by side. */
export const Palette: Story<StateDotProps> = {
  render: () => (
    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
      {[
        ['#ed4033', 'private'],
        ['#f6a437', 'pending'],
        ['#007bc1', 'published'],
      ].map(([color, label]) => (
        <span key={label} style={{ display: 'flex', alignItems: 'center' }}>
          <StateDot color={color} />
          {label}
          <span style={{ width: '0.75rem' }} />
          <StateDot color={color} outlined />
          {`${label} (outlined)`}
        </span>
      ))}
    </div>
  ),
};

/** A state with no colour at all still occupies its slot. */
export const NoColor: Story<StateDotProps> = {
  args: { color: undefined },
};
