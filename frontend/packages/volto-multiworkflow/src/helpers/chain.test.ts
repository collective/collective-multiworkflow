import { describe, expect, it } from 'vitest';
import {
  getPrimaryWorkflow,
  getAdditionalWorkflows,
  hasAdditionalWorkflows,
} from './chain';
import type { WorkflowChainEntry } from '../types';

const publication: WorkflowChainEntry = {
  workflow_id: 'simple_publication_workflow',
  title: 'Simple Publication Workflow',
  state_variable: 'review_state',
  state: { id: 'private', title: 'Private' },
  transitions: [{ '@id': 'http://x/@workflow/publish', title: 'Publish' }],
  history: [],
};

const membership: WorkflowChainEntry = {
  workflow_id: 'foundation_member_workflow',
  title: 'Foundation Member Workflow',
  state_variable: 'membership_state',
  state: { id: 'pending', title: 'Pending' },
  transitions: [{ '@id': 'http://x/@workflow/activate', title: 'Activate' }],
  history: [],
};

describe('getPrimaryWorkflow', () => {
  it('returns the first entry', () => {
    expect(getPrimaryWorkflow([publication, membership])).toBe(publication);
  });

  it('returns undefined for an empty chain', () => {
    expect(getPrimaryWorkflow([])).toBeUndefined();
  });

  it('returns undefined when the chain is absent', () => {
    expect(getPrimaryWorkflow(undefined)).toBeUndefined();
  });
});

describe('getAdditionalWorkflows', () => {
  it('returns everything after the primary', () => {
    expect(getAdditionalWorkflows([publication, membership])).toEqual([
      membership,
    ]);
  });

  it('returns nothing when only the primary is present', () => {
    expect(getAdditionalWorkflows([publication])).toEqual([]);
  });

  it('returns nothing when the chain is absent', () => {
    expect(getAdditionalWorkflows(undefined)).toEqual([]);
  });
});

describe('hasAdditionalWorkflows', () => {
  it.each([
    ['chain with a contribution', [publication, membership], true],
    ['chain with only publication', [publication], false],
    ['empty chain', [], false],
    ['absent chain', undefined, false],
  ])('%s', (_label, chain, expected) => {
    expect(hasAdditionalWorkflows(chain as WorkflowChainEntry[])).toBe(
      expected,
    );
  });
});
