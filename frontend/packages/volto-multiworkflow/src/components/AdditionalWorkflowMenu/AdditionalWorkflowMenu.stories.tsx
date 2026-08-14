/**
 * `AdditionalWorkflowMenu` renders every additional workflow of a chain.
 */

import AdditionalWorkflowMenu from './AdditionalWorkflowMenu';
import type { AdditionalWorkflowMenuProps } from './AdditionalWorkflowMenu';
import {
  multiWorkflowChain,
  publication,
  membership,
  singleWorkflowChain,
} from '../../stories/fixtures';
import type { Story, StoryMeta } from '../../stories/csf';

const meta: StoryMeta<AdditionalWorkflowMenuProps> = {
  title: 'Multiworkflow/AdditionalWorkflowMenu',
  component: AdditionalWorkflowMenu,
  args: {
    onTransition: (url: string) => {
      // Stories are static; log rather than navigate.
      // eslint-disable-next-line no-console
      console.log('transition', url);
    },
  },
  parameters: {
    docs: {
      description: {
        component:
          'Presentational: it takes the `chain` key of the `@workflow` payload ' +
          'and a callback. The first entry of a chain is the publication ' +
          'workflow, which this menu never renders — it belongs to the control ' +
          'Plone already has.',
      },
    },
  },
};

export default meta;

/** Two additional workflows, one of which offers a transition. */
export const TwoWorkflows: Story<AdditionalWorkflowMenuProps> = {
  args: { chain: multiWorkflowChain },
};

/** A single additional workflow. */
export const OneWorkflow: Story<AdditionalWorkflowMenuProps> = {
  args: { chain: [publication, membership] },
};

/**
 * Content without additional workflows renders **nothing at all**.
 *
 * This is the story to look at when asking what the add-on does to a vanilla
 * site: the chain holds only the publication workflow, and the output is empty.
 */
export const NoAdditionalWorkflows: Story<AdditionalWorkflowMenuProps> = {
  args: { chain: singleWorkflowChain },
};

/** An absent `chain` key, which is what non-participating content serves. */
export const AbsentChain: Story<AdditionalWorkflowMenuProps> = {
  args: { chain: undefined },
};

/** While a transition is in flight, the buttons are disabled. */
export const Disabled: Story<AdditionalWorkflowMenuProps> = {
  args: { chain: multiWorkflowChain, disabled: true },
};
