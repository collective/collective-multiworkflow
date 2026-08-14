import { describe, expect, it } from 'vitest';
import {
  getWorkflowTitles,
  markCurrentVersion,
  spansMultipleWorkflows,
  threadPreviousStates,
} from './history';
import type { HistoryEntry, WorkflowChainEntry } from '../types';

const PUBLICATION = 'simple_publication_workflow';
const MEMBERSHIP = 'foundation_member_workflow';

/**
 * Build a workflow entry.
 *
 * Defaults mirror what the backend emits: a creation entry carries no
 * `action`, every other one does.
 */
function workflowEntry(
  workflow_id: string,
  state_title: string,
  overrides: Partial<HistoryEntry> = {},
): HistoryEntry {
  return {
    type: 'workflow',
    workflow_id,
    action: 'some_transition',
    transition_title: `To ${state_title}`,
    state_title,
    actor: { fullname: 'John Doe' },
    time: '2026-08-13T10:00:00+00:00',
    ...overrides,
  };
}

function versioningEntry(version: number): HistoryEntry {
  return {
    type: 'versioning',
    workflow_id: null,
    version,
    transition_title: 'Edited',
    actor: { fullname: 'John Doe' },
    time: '2026-08-13T10:00:00+00:00',
  };
}

describe('threadPreviousStates', () => {
  // Newest first, as `@history` serves it. Read bottom-up, the publication
  // workflow went Private → Published and the membership one Pending → Active,
  // and the two interleave.
  const merged: HistoryEntry[] = [
    workflowEntry(MEMBERSHIP, 'Active'),
    workflowEntry(PUBLICATION, 'Published'),
    workflowEntry(MEMBERSHIP, 'Pending', { action: null }),
    workflowEntry(PUBLICATION, 'Private', { action: null }),
  ];

  it('threads each workflow through its own states', () => {
    const [active, published] = threadPreviousStates(merged);

    expect(active.prev_state_title).toBe('Pending');
    expect(published.prev_state_title).toBe('Private');
  });

  it('never derives a previous state from another workflow', () => {
    // The regression this exists for: entry 0 is preceded in the *list* by a
    // publication entry, and reading that one would claim the membership
    // workflow moved from Published to Active.
    const [active] = threadPreviousStates(merged);

    expect(active.prev_state_title).not.toBe('Published');
  });

  it("leaves each workflow's first entry without a previous state", () => {
    const [, , pending, priv] = threadPreviousStates(merged);

    expect(pending.prev_state_title).toBeUndefined();
    expect(priv.prev_state_title).toBeUndefined();
  });

  it('preserves the order it was given', () => {
    const threaded = threadPreviousStates(merged);

    expect(threaded.map((entry) => entry.state_title)).toEqual([
      'Active',
      'Published',
      'Pending',
      'Private',
    ]);
  });

  it('does not modify the entries it was given', () => {
    // They belong to the reducer; upstream annotates them in place.
    threadPreviousStates(merged);

    expect(merged.every((entry) => !('prev_state_title' in entry))).toBe(true);
  });

  it('carries a state across entries that record none', () => {
    // A versioning entry sits in its own bucket and interrupts nothing.
    const withVersioning: HistoryEntry[] = [
      workflowEntry(PUBLICATION, 'Published'),
      versioningEntry(1),
      workflowEntry(PUBLICATION, 'Private', { action: null }),
    ];

    const [published] = threadPreviousStates(withVersioning);

    expect(published.prev_state_title).toBe('Private');
  });

  it('behaves as upstream does for a single workflow', () => {
    const linear: HistoryEntry[] = [
      workflowEntry(PUBLICATION, 'Published'),
      workflowEntry(PUBLICATION, 'Pending review'),
      workflowEntry(PUBLICATION, 'Private', { action: null }),
    ];

    expect(
      threadPreviousStates(linear).map((entry) => entry.prev_state_title),
    ).toEqual(['Pending review', 'Private', undefined]);
  });

  it('handles an empty history', () => {
    expect(threadPreviousStates([])).toEqual([]);
  });
});

describe('markCurrentVersion', () => {
  it('marks the most recent versioning entry', () => {
    const entries = [
      workflowEntry(PUBLICATION, 'Published'),
      versioningEntry(2),
      versioningEntry(1),
    ];

    const marked = markCurrentVersion(entries);

    expect(marked[1].is_current).toBe(true);
    expect(marked[2].is_current).toBeUndefined();
  });

  it('leaves a history with no versioning entry alone', () => {
    const entries = [workflowEntry(PUBLICATION, 'Published')];

    expect(markCurrentVersion(entries)).toBe(entries);
  });
});

describe('spansMultipleWorkflows', () => {
  it('is true when two workflows recorded entries', () => {
    expect(
      spansMultipleWorkflows([
        workflowEntry(MEMBERSHIP, 'Active'),
        workflowEntry(PUBLICATION, 'Published'),
      ]),
    ).toBe(true);
  });

  it('is false for one workflow plus versioning entries', () => {
    // The case on every site without this add-on: the column stays hidden.
    expect(
      spansMultipleWorkflows([
        workflowEntry(PUBLICATION, 'Published'),
        versioningEntry(1),
      ]),
    ).toBe(false);
  });

  it('is false for an empty history', () => {
    expect(spansMultipleWorkflows([])).toBe(false);
  });
});

describe('getWorkflowTitles', () => {
  const chain: WorkflowChainEntry[] = [
    {
      workflow_id: PUBLICATION,
      title: 'Simple Publication Workflow',
      state_variable: 'review_state',
      state: { id: 'private', title: 'Private' },
      transitions: [],
      history: [],
    },
    {
      workflow_id: MEMBERSHIP,
      title: 'Membership',
      state_variable: 'workflow_states',
      state: { id: 'pending', title: 'Pending' },
      transitions: [],
      history: [],
    },
  ];

  it('maps ids to titles', () => {
    expect(getWorkflowTitles(chain)).toEqual({
      [PUBLICATION]: 'Simple Publication Workflow',
      [MEMBERSHIP]: 'Membership',
    });
  });

  it('is empty when there is no chain', () => {
    expect(getWorkflowTitles(undefined)).toEqual({});
  });
});
