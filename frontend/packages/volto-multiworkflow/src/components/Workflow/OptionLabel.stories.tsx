/**
 * `OptionLabel` is the contents of one row in the workflow select.
 */

import OptionLabel from './OptionLabel';
import type { OptionLabelProps } from './OptionLabel';
import type { Story, StoryMeta } from '../../stories/csf';

const meta: StoryMeta<OptionLabelProps> = {
  title: 'Multiworkflow/Workflow/OptionLabel',
  component: OptionLabel,
  args: { label: 'Published', color: '#007bc1' },
  decorators: [
    // react-select gives each option a flex row; reproduce it so the check
    // mark sits where it does in the real control.
    (Story) => (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          minHeight: '50px',
          padding: '12px',
          maxWidth: '320px',
          borderBottom: '1px solid #ececec',
        }}
      >
        <Story />
      </div>
    ),
  ],
  parameters: {
    docs: {
      description: {
        component:
          'Rendered inside react-select’s `Option`, which supplies the ' +
          '`isSelected` and `isFocused` flags. Kept separate from that ' +
          'component so the row can be seen without the library, which is ' +
          'loaded lazily and is not resolvable in Storybook.',
      },
    },
  },
};

export default meta;

/** An option that is neither selected nor focused. */
export const Default: Story<OptionLabelProps> = {
  args: {},
};

/** The state the object is currently in: the dot is filled. */
export const Current: Story<OptionLabelProps> = {
  args: { isCurrent: true },
};

/** Selected — the check mark takes the accent colour. */
export const Selected: Story<OptionLabelProps> = {
  args: { isCurrent: true, isSelected: true },
};

/** Focused but not selected — a muted check mark previews the choice. */
export const Focused: Story<OptionLabelProps> = {
  args: { isFocused: true },
};

/** Every row of a menu at once, in the order react-select would draw them. */
export const Menu: Story<OptionLabelProps> = {
  render: () => (
    <div style={{ width: '100%' }}>
      <OptionLabel label="Retract" color="#ed4033" isFocused />
      <OptionLabel label="Reject" color="#f6a437" />
      <OptionLabel label="Published" color="#007bc1" isCurrent isSelected />
    </div>
  ),
};
