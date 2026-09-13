import type { ConfigType } from '@plone/registry';
import installSettings from './config/settings';
import installReducers from './config/reducers';

function applyConfig(config: ConfigType) {
  installSettings(config);
  installReducers(config);

  return config;
}

export default applyConfig;

export { default as AdditionalWorkflow } from './components/AdditionalWorkflow/AdditionalWorkflow';
export { default as AdditionalWorkflowMenu } from './components/AdditionalWorkflowMenu/AdditionalWorkflowMenu';
export { default as StateBadge } from './components/StateBadge/StateBadge';
export {
  getMultiWorkflow,
  transitionMultiWorkflow,
} from './actions/multiworkflow';
export {
  getPrimaryWorkflow,
  getAdditionalWorkflows,
  hasAdditionalWorkflows,
} from './helpers/chain';
export {
  getWorkflowTitles,
  markCurrentVersion,
  spansMultipleWorkflows,
  threadPreviousStates,
} from './helpers/history';
export {
  WORKFLOW_STATE_SEPARATOR,
  WORKFLOW_STATES_VOCABULARY,
  formatWorkflowState,
  getAdditionalWorkflowStates,
  getWorkflowStates,
  parseWorkflowState,
} from './helpers/states';
export type {
  HistoryEntry,
  MultiWorkflowState,
  ParsedWorkflowState,
  WithWorkflowStates,
  WorkflowChainEntry,
  WorkflowInfo,
  WorkflowState,
  WorkflowStateValue,
  WorkflowTransition,
} from './types';
