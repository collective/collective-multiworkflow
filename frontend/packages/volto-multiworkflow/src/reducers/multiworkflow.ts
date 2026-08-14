/**
 * Reducer holding the workflow chain of the current content object.
 */

import {
  GET_MULTIWORKFLOW,
  TRANSITION_MULTIWORKFLOW,
} from '../actions/multiworkflow';
import type { MultiWorkflowState, WorkflowChainEntry } from '../types';

const initialState: MultiWorkflowState = {
  loading: false,
  loaded: false,
  error: null,
  chain: [],
};

interface Action {
  type: string;
  result?: { chain?: WorkflowChainEntry[] };
  error?: unknown;
}

/**
 * Keep the `chain` key from the `@workflow` payload.
 *
 * Content without additional workflows has no `chain`, which is reduced to an
 * empty array so consumers can render nothing without special-casing.
 */
export default function multiworkflow(
  state: MultiWorkflowState = initialState,
  action: Action = { type: '' },
): MultiWorkflowState {
  switch (action.type) {
    case `${GET_MULTIWORKFLOW}_PENDING`:
    case `${TRANSITION_MULTIWORKFLOW}_PENDING`:
      return { ...state, loading: true, loaded: false, error: null };

    case `${GET_MULTIWORKFLOW}_SUCCESS`:
      return {
        ...state,
        loading: false,
        loaded: true,
        error: null,
        chain: action.result?.chain ?? [],
      };

    // A transition's response is the last review_history entry, not a workflow
    // payload — there is no chain in it. Keep the one we have; the component
    // re-fetches to pick up the new states.
    case `${TRANSITION_MULTIWORKFLOW}_SUCCESS`:
      return { ...state, loading: false, loaded: true, error: null };

    case `${GET_MULTIWORKFLOW}_FAIL`:
      return {
        ...state,
        loading: false,
        loaded: false,
        error: action.error ?? null,
        chain: [],
      };

    // A failed transition leaves the object where it was, so the chain we are
    // holding is still accurate.
    case `${TRANSITION_MULTIWORKFLOW}_FAIL`:
      return {
        ...state,
        loading: false,
        error: action.error ?? null,
      };

    default:
      return state;
  }
}
