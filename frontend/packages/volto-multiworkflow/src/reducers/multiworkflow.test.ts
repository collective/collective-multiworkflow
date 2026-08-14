import { describe, expect, it } from 'vitest';
import multiworkflow from './multiworkflow';
import {
  GET_MULTIWORKFLOW,
  TRANSITION_MULTIWORKFLOW,
} from '../actions/multiworkflow';
import type { WorkflowChainEntry } from '../types';

const entry: WorkflowChainEntry = {
  workflow_id: 'foundation_member_workflow',
  title: 'Foundation Member Workflow',
  state_variable: 'membership_state',
  state: { id: 'pending', title: 'Pending' },
  transitions: [],
  history: [],
};

describe('multiworkflow reducer', () => {
  it('starts empty', () => {
    const state = multiworkflow(undefined);

    expect(state).toEqual({
      loading: false,
      loaded: false,
      error: null,
      chain: [],
    });
  });

  it('marks loading while pending', () => {
    const state = multiworkflow(undefined, {
      type: `${GET_MULTIWORKFLOW}_PENDING`,
    });

    expect(state.loading).toBe(true);
    expect(state.loaded).toBe(false);
  });

  it('stores the chain on success', () => {
    const state = multiworkflow(undefined, {
      type: `${GET_MULTIWORKFLOW}_SUCCESS`,
      result: { chain: [entry] },
    });

    expect(state.chain).toEqual([entry]);
    expect(state.loaded).toBe(true);
    expect(state.loading).toBe(false);
  });

  it('reduces a payload without a chain to an empty list', () => {
    const state = multiworkflow(undefined, {
      type: `${GET_MULTIWORKFLOW}_SUCCESS`,
      result: {},
    });

    expect(state.chain).toEqual([]);
    expect(state.loaded).toBe(true);
  });

  it('keeps the chain after a transition', () => {
    // The transition endpoint answers with the last review_history entry, not
    // a workflow payload — reducing its response would wipe the chain and make
    // the menu disappear after one click.
    const before = multiworkflow(undefined, {
      type: `${GET_MULTIWORKFLOW}_SUCCESS`,
      result: { chain: [entry] },
    });
    const after = multiworkflow(before, {
      type: `${TRANSITION_MULTIWORKFLOW}_SUCCESS`,
      result: { review_state: 'private' } as never,
    });

    expect(after.chain).toEqual([entry]);
    expect(after.loading).toBe(false);
  });

  it('keeps the chain when a transition fails', () => {
    const before = multiworkflow(undefined, {
      type: `${GET_MULTIWORKFLOW}_SUCCESS`,
      result: { chain: [entry] },
    });
    const after = multiworkflow(before, {
      type: `${TRANSITION_MULTIWORKFLOW}_FAIL`,
      error: 'boom',
    });

    expect(after.chain).toEqual([entry]);
    expect(after.error).toBe('boom');
  });

  it('clears the chain and records the error when the fetch fails', () => {
    const before = multiworkflow(undefined, {
      type: `${GET_MULTIWORKFLOW}_SUCCESS`,
      result: { chain: [entry] },
    });
    const after = multiworkflow(before, {
      type: `${GET_MULTIWORKFLOW}_FAIL`,
      error: 'boom',
    });

    expect(after.chain).toEqual([]);
    expect(after.error).toBe('boom');
    expect(after.loaded).toBe(false);
  });

  it('ignores unrelated actions', () => {
    const before = multiworkflow(undefined, {
      type: `${GET_MULTIWORKFLOW}_SUCCESS`,
      result: { chain: [entry] },
    });

    expect(multiworkflow(before, { type: 'SOMETHING_ELSE' })).toBe(before);
  });
});
