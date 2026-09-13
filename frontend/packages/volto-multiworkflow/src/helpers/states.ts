/**
 * Helpers for the `workflow_states` values the backend serializes.
 *
 * Every Dexterity object's serialization, and each summary of a catalog
 * result, carries a `workflow_states` list: the object's state in every
 * workflow of its chain, as `<workflow-id>|<state-id>`, in chain order. Unlike
 * the `@workflow` payload it holds ids only, but it arrives with the object or
 * the listing itself, so reading it costs no further request.
 *
 * These mirror `collective.multiworkflow.utils.workflow` on the backend. Build
 * and split values through them rather than by hand.
 */

import type {
  ParsedWorkflowState,
  WithWorkflowStates,
  WorkflowStateValue,
} from '../types';

/** Separates the workflow id from the state id within one value. */
export const WORKFLOW_STATE_SEPARATOR = '|';

/**
 * The vocabulary holding one term per state of every workflow.
 *
 * Its tokens are `workflow_states` values and its titles read
 * `<workflow>: <state>`, naming the workflow by any label declared for it. It
 * is readable by anyone who can view the context, which makes it the source of
 * a translated label for a value.
 */
export const WORKFLOW_STATES_VOCABULARY =
  'collective.multiworkflow.vocabularies.WorkflowStates';

/**
 * Build one value out of a workflow id and a state id.
 *
 * @param workflowId Id of the workflow the state belongs to.
 * @param stateId Id of the state that workflow is in.
 * @returns The value as the backend serializes it.
 */
export function formatWorkflowState(
  workflowId: string,
  stateId: string,
): WorkflowStateValue {
  return `${workflowId}${WORKFLOW_STATE_SEPARATOR}${stateId}`;
}

/**
 * Split one value into its workflow id and state id.
 *
 * Splits at the first separator, as the backend does. Neither id can contain
 * one, since both are Zope ids.
 *
 * @param value A value as the backend serializes it.
 * @returns The two ids, or `undefined` for a value carrying no separator. The
 *   backend never serves one, so a listing can skip it rather than fail to
 *   render.
 */
export function parseWorkflowState(
  value: WorkflowStateValue,
): ParsedWorkflowState | undefined {
  const index = value.indexOf(WORKFLOW_STATE_SEPARATOR);
  if (index === -1) {
    return undefined;
  }
  return {
    workflow_id: value.slice(0, index),
    state_id: value.slice(index + 1),
  };
}

/**
 * The object's state in every workflow of its chain.
 *
 * @param item A content object or a catalog summary, as the backend serializes
 *   it.
 * @returns Its `workflow_states` values in chain order, the primary workflow
 *   first. Empty when the item carries no such key.
 */
export function getWorkflowStates(
  item?: WithWorkflowStates | null,
): WorkflowStateValue[] {
  return item?.workflow_states ?? [];
}

/**
 * The object's state in its additional workflows only.
 *
 * The first value always belongs to the workflow driving `review_state`,
 * which a listing usually shows already.
 *
 * @param item A content object or a catalog summary, as the backend serializes
 *   it.
 * @returns Every value after the first. Empty for content with no additional
 *   workflow, and when the item carries no `workflow_states` at all.
 */
export function getAdditionalWorkflowStates(
  item?: WithWorkflowStates | null,
): WorkflowStateValue[] {
  return getWorkflowStates(item).slice(1);
}
