/**
 * Payload fixtures shared by the stories.
 *
 * Shaped exactly like what the backend serves, so a story that looks right is
 * evidence the component handles the real contract. The values match the
 * add-on's own example content: a publication workflow plus a membership one.
 */

import type { HistoryEntry, WorkflowChainEntry } from '../types';

/** The workflow every Plone object already has. */
export const publication: WorkflowChainEntry = {
  workflow_id: 'simple_publication_workflow',
  title: 'Simple Publication Workflow',
  state_variable: 'review_state',
  state: { id: 'published', title: 'Published' },
  transitions: [
    {
      '@id': 'http://localhost:8080/Plone/doc/@workflow/retract',
      title: 'Retract',
    },
    {
      '@id': 'http://localhost:8080/Plone/doc/@workflow/reject',
      title: 'Reject',
    },
  ],
  history: [],
};

/** A contributed workflow, in a state of its own. */
export const membership: WorkflowChainEntry = {
  workflow_id: 'foundation_member_workflow',
  title: 'Membership',
  state_variable: 'workflow_states',
  state: { id: 'active', title: 'Active' },
  transitions: [
    {
      '@id': 'http://localhost:8080/Plone/doc/@workflow/lapse',
      title: 'Lapse membership',
    },
  ],
  history: [],
};

/** A second contributed workflow, with nothing available to the user. */
export const review: WorkflowChainEntry = {
  workflow_id: 'editorial_review_workflow',
  title: 'Editorial review',
  state_variable: 'workflow_states',
  state: { id: 'awaiting_review', title: 'Awaiting review' },
  transitions: [],
  history: [],
};

/** What a site without this add-on serves: one workflow, no `chain` key. */
export const singleWorkflowChain: WorkflowChainEntry[] = [publication];

/** What participating content serves. */
export const multiWorkflowChain: WorkflowChainEntry[] = [
  publication,
  membership,
  review,
];

const actor = { fullname: 'Ada Lovelace', username: 'ada' };

/**
 * A merged history, newest first, already threaded by `helpers/history`.
 *
 * Deliberately interleaves two workflows and a versioning entry, because that
 * is the arrangement upstream's row-to-row threading gets wrong.
 */
export const mergedHistory: HistoryEntry[] = [
  {
    type: 'workflow',
    workflow_id: 'foundation_member_workflow',
    action: 'activate',
    transition_title: 'Activate membership',
    state_title: 'Active',
    prev_state_title: 'Pending',
    actor,
    time: '2026-08-13T17:30:00+00:00',
    comments: 'Renewed for 2026',
  },
  {
    type: 'versioning',
    workflow_id: null,
    action: 'Edited',
    transition_title: 'Edited',
    actor,
    time: '2026-08-13T16:10:00+00:00',
    comments: 'Fixed a typo',
    version: 1,
    may_revert: true,
    is_current: true,
  },
  {
    type: 'workflow',
    workflow_id: 'simple_publication_workflow',
    action: 'publish',
    transition_title: 'Publish',
    state_title: 'Published',
    prev_state_title: 'Private',
    actor,
    time: '2026-08-13T15:00:00+00:00',
    comments: '',
  },
  {
    type: 'versioning',
    workflow_id: null,
    action: 'Edited',
    transition_title: 'Edited',
    actor,
    time: '2026-08-13T14:00:00+00:00',
    comments: 'Initial version',
    version: 0,
    may_revert: true,
  },
  {
    type: 'workflow',
    workflow_id: 'foundation_member_workflow',
    action: null,
    transition_title: 'Create',
    state_title: 'Pending',
    actor,
    time: '2026-08-13T13:00:00+00:00',
    comments: '',
  },
  {
    type: 'workflow',
    workflow_id: 'simple_publication_workflow',
    action: null,
    transition_title: 'Create',
    state_title: 'Private',
    actor,
    time: '2026-08-13T13:00:00+00:00',
    comments: '',
  },
];

/** The same history as a site without additional workflows produces. */
export const singleWorkflowHistory: HistoryEntry[] = mergedHistory.filter(
  (entry) =>
    entry.workflow_id === 'simple_publication_workflow' ||
    entry.workflow_id === null,
);

/** Workflow id to title, as the History view derives it from the chain. */
export const workflowTitles: Record<string, string> = {
  simple_publication_workflow: 'Simple Publication Workflow',
  foundation_member_workflow: 'Membership',
};
