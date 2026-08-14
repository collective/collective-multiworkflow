/**
 * The workflow control, rendering one selector per workflow in the chain.
 *
 * A TypeScript port of `@plone/volto`'s `components/manage/Workflow/Workflow`,
 * with two added blocks marked `--- collective.multiworkflow ---`. Kept close
 * to upstream so a Volto upgrade stays a small diff: re-read the original and
 * re-apply those two blocks.
 *
 * With no additional workflows — every object on a site without this add-on —
 * the extra block renders nothing and the component behaves exactly as upstream.
 *
 * This file is the container: store reads, effects, and the two transition
 * handlers. Everything it draws lives in `WorkflowSelect` and the components
 * that one composes.
 */

import { useEffect } from 'react';
import { compose } from 'redux';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';
import { toast } from 'react-toastify';
import { defineMessages, useIntl } from 'react-intl';

import Toast from '@plone/volto/components/manage/Toast/Toast';
import { flattenToAppURL } from '@plone/volto/helpers/Url/Url';
import { getCurrentStateMapping } from '@plone/volto/helpers/Workflows/Workflows';
import { injectLazyLibs } from '@plone/volto/helpers/Loadable/Loadable';

import { getContent } from '@plone/volto/actions/content/content';
import {
  getWorkflow,
  transitionWorkflow,
} from '@plone/volto/actions/workflow/workflow';

import WorkflowSelect from './WorkflowSelect';
import type { SelectRenderProps, WorkflowOption } from './types';

// --- collective.multiworkflow (1/2): imports ---
import {
  getMultiWorkflow,
  transitionMultiWorkflow,
} from '@plone-collective/volto-multiworkflow/actions/multiworkflow';
import { getAdditionalWorkflows } from '@plone-collective/volto-multiworkflow/helpers/chain';
import type {
  MultiWorkflowState,
  WorkflowState,
  WorkflowTransition,
} from '@plone-collective/volto-multiworkflow/types';
// --- end collective.multiworkflow ---

/** The slice of the store this control reads. */
interface StoreShape {
  workflow: {
    history: unknown[];
    transitions: WorkflowTransition[];
    transition: { loaded: boolean };
    currentState: WorkflowState;
  };
  content?: { data?: { review_state?: string | null } };
  multiworkflow?: MultiWorkflowState;
}

export interface WorkflowProps {
  /** Path of the content object whose workflows are managed. */
  pathname: string;
  /** Injected by `injectLazyLibs(['reactSelect'])`. */
  reactSelect: SelectRenderProps['reactSelect'];
}

const messages = defineMessages({
  messageUpdated: {
    id: 'Workflow updated.',
    defaultMessage: 'Workflow updated.',
  },
  messageNoWorkflow: {
    id: 'No workflow',
    defaultMessage: 'No workflow',
  },
  state: {
    id: 'State',
    defaultMessage: 'State',
  },
});

function useWorkflow() {
  const history = useSelector(
    (state: StoreShape) => state.workflow.history,
    shallowEqual,
  );
  const transitions = useSelector(
    (state: StoreShape) => state.workflow.transitions,
    shallowEqual,
  );
  const loaded = useSelector(
    (state: StoreShape) => state.workflow.transition.loaded,
  );
  const currentStateValue = useSelector(
    (state: StoreShape) =>
      getCurrentStateMapping(state.workflow.currentState) as WorkflowOption,
    shallowEqual,
  );

  return { loaded, history, transitions, currentStateValue };
}

const Workflow = (props: WorkflowProps) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const { loaded, transitions, currentStateValue } = useWorkflow();
  const content = useSelector(
    (state: StoreShape) => state.content?.data,
    shallowEqual,
  );
  const { pathname } = props;

  // --- collective.multiworkflow (2a/2): chain state and handler ---
  const chain = useSelector(
    (state: StoreShape) => state.multiworkflow?.chain ?? [],
    shallowEqual,
  );
  const additionalWorkflows = getAdditionalWorkflows(chain);

  const transitionAdditional = (selectedOption: WorkflowOption) => {
    // The transition endpoint replies with the last review_history entry, not
    // a workflow payload, so the chain has to be re-read afterwards.
    Promise.resolve(
      dispatch(transitionMultiWorkflow(selectedOption.url as string) as never),
    ).then(() => {
      dispatch(getMultiWorkflow(pathname) as never);
      dispatch(getContent(pathname) as never);
    });
    toast.success(
      <Toast
        success
        title={intl.formatMessage(messages.messageUpdated)}
        content=""
      />,
    );
  };
  // --- end collective.multiworkflow ---

  useEffect(() => {
    dispatch(getWorkflow(pathname) as never);
    dispatch(getContent(pathname) as never);
    // collective.multiworkflow: read the full chain alongside core's payload.
    dispatch(getMultiWorkflow(pathname) as never);
  }, [dispatch, pathname, loaded]);

  const transition = (selectedOption: WorkflowOption) => {
    dispatch(
      transitionWorkflow(
        flattenToAppURL(selectedOption.url as string),
      ) as never,
    );
    toast.success(
      <Toast
        success
        title={intl.formatMessage(messages.messageUpdated)}
        content=""
      />,
    );
  };

  const { Placeholder } = props.reactSelect.components;
  const Select = props.reactSelect.default;

  return (
    <>
      <WorkflowSelect
        id="state-select"
        title={intl.formatMessage(messages.state)}
        transitions={transitions}
        isDisabled={!content?.review_state || transitions.length === 0}
        onChange={transition}
        value={
          content?.review_state
            ? currentStateValue
            : {
                label: intl.formatMessage(messages.messageNoWorkflow),
                value: 'noworkflow',
              }
        }
        Select={Select}
        Placeholder={Placeholder}
        intl={intl}
        {...props}
      />

      {/* --- collective.multiworkflow (2b/2): one selector per additional
          workflow, rendered inside the same control. Empty for every object
          that has no additional workflows. --- */}
      {additionalWorkflows.map((entry) => (
        <WorkflowSelect
          key={entry.workflow_id}
          id={`state-select-${entry.workflow_id}`}
          title={entry.title}
          transitions={entry.transitions}
          isDisabled={entry.transitions.length === 0}
          onChange={transitionAdditional}
          value={getCurrentStateMapping(entry.state) as WorkflowOption}
          Select={Select}
          Placeholder={Placeholder}
          intl={intl}
          {...props}
        />
      ))}
      {/* --- end collective.multiworkflow --- */}
    </>
  );
};

export default compose(injectLazyLibs(['reactSelect']))(Workflow);
