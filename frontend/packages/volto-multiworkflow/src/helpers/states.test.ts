import { describe, expect, it } from 'vitest';
import {
  WORKFLOW_STATE_SEPARATOR,
  formatWorkflowState,
  getAdditionalWorkflowStates,
  getWorkflowStates,
  parseWorkflowState,
} from './states';
import type { WithWorkflowStates } from '../types';

const PUBLISHED = 'simple_publication_workflow|published';
const ACTIVE = 'foundation_member_workflow|active';

describe('formatWorkflowState', () => {
  it('joins the ids with the separator', () => {
    expect(formatWorkflowState('foundation_member_workflow', 'active')).toBe(
      ACTIVE,
    );
  });

  it('uses the separator the backend uses', () => {
    expect(WORKFLOW_STATE_SEPARATOR).toBe('|');
  });
});

describe('parseWorkflowState', () => {
  it('splits a value into its ids', () => {
    expect(parseWorkflowState(ACTIVE)).toEqual({
      workflow_id: 'foundation_member_workflow',
      state_id: 'active',
    });
  });

  it('reads back what formatWorkflowState builds', () => {
    const value = formatWorkflowState('simple_publication_workflow', 'private');

    expect(parseWorkflowState(value)).toEqual({
      workflow_id: 'simple_publication_workflow',
      state_id: 'private',
    });
  });

  it('splits at the first separator, as the backend does', () => {
    expect(parseWorkflowState('a|b|c')).toEqual({
      workflow_id: 'a',
      state_id: 'b|c',
    });
  });

  it('returns undefined for a bare state id', () => {
    expect(parseWorkflowState('published')).toBeUndefined();
  });
});

describe('getWorkflowStates', () => {
  it('returns the values in chain order', () => {
    expect(getWorkflowStates({ workflow_states: [PUBLISHED, ACTIVE] })).toEqual(
      [PUBLISHED, ACTIVE],
    );
  });

  it.each([
    ['an item without the key', {}],
    ['an absent item', undefined],
    ['a null item', null],
  ])('is empty for %s', (_label, item) => {
    expect(getWorkflowStates(item as WithWorkflowStates | null)).toEqual([]);
  });
});

describe('getAdditionalWorkflowStates', () => {
  it('drops the primary workflow', () => {
    expect(
      getAdditionalWorkflowStates({ workflow_states: [PUBLISHED, ACTIVE] }),
    ).toEqual([ACTIVE]);
  });

  it('is empty when only the primary workflow is present', () => {
    expect(
      getAdditionalWorkflowStates({ workflow_states: [PUBLISHED] }),
    ).toEqual([]);
  });

  it('is empty when the key is absent', () => {
    expect(getAdditionalWorkflowStates({})).toEqual([]);
  });
});
