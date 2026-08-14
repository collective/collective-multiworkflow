/**
 * `AdditionalWorkflow` is the store-connected wrapper around the menu.
 *
 * The stories supply a static store, so what they show is the chain the
 * fixture describes. Transitions do not resolve: `dispatch` is inert here, by
 * design — see `stories/withStore`.
 */

import AdditionalWorkflow from './AdditionalWorkflow';
import type { AdditionalWorkflowProps } from './AdditionalWorkflow';
import {
  multiWorkflowChain,
  singleWorkflowChain,
} from '../../stories/fixtures';
import { withStore } from '../../stories/withStore';
import type { Story, StoryMeta } from '../../stories/csf';

const meta: StoryMeta<AdditionalWorkflowProps> = {
  title: 'Multiworkflow/AdditionalWorkflow',
  component: AdditionalWorkflow,
  args: { url: '/doc' },
  parameters: {
    docs: {
      description: {
        component:
          'Reads the chain from the store and re-fetches after a transition, ' +
          'because plone.restapi answers a transition with the last ' +
          '`review_history` entry rather than the workflow payload.',
      },
    },
  },
};

export default meta;

/** Content participating in two additional workflows. */
export const WithChain: Story<AdditionalWorkflowProps> = {
  decorators: [
    withStore({
      multiworkflow: {
        loading: false,
        loaded: true,
        error: null,
        chain: multiWorkflowChain,
      },
    }),
  ],
};

/** Content with no additional workflows: the wrapper renders nothing. */
export const WithoutAdditionalWorkflows: Story<AdditionalWorkflowProps> = {
  decorators: [
    withStore({
      multiworkflow: {
        loading: false,
        loaded: true,
        error: null,
        chain: singleWorkflowChain,
      },
    }),
  ],
};

/** A transition in flight disables every button. */
export const Loading: Story<AdditionalWorkflowProps> = {
  decorators: [
    withStore({
      multiworkflow: {
        loading: true,
        loaded: false,
        error: null,
        chain: multiWorkflowChain,
      },
    }),
  ],
};
