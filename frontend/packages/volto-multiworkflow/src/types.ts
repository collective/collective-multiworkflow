/**
 * The `@workflow` payload contract, as served by `collective.multiworkflow`.
 *
 * These interfaces mirror the backend serializer exactly and are the single
 * source of truth for consumers of this add-on. They must be updated in the
 * same commit as any serializer change.
 */

/** A workflow state, as reported for one workflow in the chain. */
export interface WorkflowState {
  /** State id, e.g. `pending`. */
  id: string;
  /** Human-readable, translated title. */
  title: string;
}

/** A transition available to the current user. */
export interface WorkflowTransition {
  /** URL to POST to in order to execute the transition. */
  '@id': string;
  /** Human-readable, translated title. */
  title: string;
}

/** One entry of a content object's workflow chain. */
export interface WorkflowChainEntry {
  /** Workflow id, e.g. `foundation_member_workflow`. */
  workflow_id: string;
  /**
   * Human-readable, translated name of the workflow: the `label` its
   * registration declares, or the workflow's own title when none is declared.
   */
  title: string;
  /** The variable this workflow drives; never `review_state` for secondaries. */
  state_variable: string;
  /** The object's current state in this workflow. */
  state: WorkflowState;
  /** Transitions of this workflow available to the current user. */
  transitions: WorkflowTransition[];
  /** This workflow's history entries; empty when it records none. */
  history: Array<Record<string, unknown>>;
}

/**
 * One entry of the `@history` endpoint response.
 *
 * Shaped by core's `HistoryGet` for versioning entries and by this add-on's
 * `ChainHistoryViewlet` for workflow ones. The index signature is deliberate:
 * core adds keys this add-on does not model, and the History view passes
 * entries through untouched.
 */
export interface HistoryEntry {
  /** `workflow`, `versioning`, and whatever else core grows. */
  type: string;
  /**
   * The workflow that recorded the transition, `null` for entries that belong
   * to no workflow at all — versioning ones, above all.
   *
   * This is what makes a merged history readable: without it, consecutive
   * entries cannot be told apart by workflow and a state transition appears to
   * follow whichever entry happens to precede it.
   */
  workflow_id: string | null;
  /** Transition id; absent or `null` on the creation entry. */
  action?: string | null;
  /** Translated label for the transition. */
  transition_title?: string;
  /** Translated label for the state the entry moved *to*. */
  state_title?: string;
  /** Translated label for the state it moved *from*; computed client-side. */
  prev_state_title?: string;
  actor: { fullname?: string; username?: string };
  time: string;
  comments?: string;
  version?: number;
  may_revert?: boolean;
  is_current?: boolean;
  [key: string]: unknown;
}

/**
 * The `@workflow` endpoint response.
 *
 * `chain` is present only for content that participates in additional
 * workflows; everything else is the payload Plone has always served.
 */
export interface WorkflowInfo {
  '@id'?: string;
  state?: WorkflowState;
  transitions?: WorkflowTransition[];
  history?: Array<Record<string, unknown>>;
  chain?: WorkflowChainEntry[];
}

/**
 * One `workflow_states` value: `<workflow-id>|<state-id>`.
 *
 * The same form the backend's `workflow_states` catalog index holds, and the
 * token of the workflow states vocabulary.
 */
export type WorkflowStateValue = string;

/** A `workflow_states` value split into its ids. */
export interface ParsedWorkflowState {
  /** Workflow id, e.g. `foundation_member_workflow`. */
  workflow_id: string;
  /** Id of the state that workflow is in, e.g. `pending`. */
  state_id: string;
}

/**
 * Anything the backend serializes with a `workflow_states` key.
 *
 * Every Dexterity object's serialization carries it, and so does each summary
 * of a catalog result — a `@search` item, or a folder's `items`.
 */
export interface WithWorkflowStates {
  /**
   * The object's state in every workflow of its chain, in chain order: the
   * primary workflow first. Absent from a backend that predates the key.
   */
  workflow_states?: WorkflowStateValue[];
}

/** Shape this add-on contributes to the Redux store. */
export interface MultiWorkflowState {
  loading: boolean;
  loaded: boolean;
  error: unknown | null;
  chain: WorkflowChainEntry[];
}
