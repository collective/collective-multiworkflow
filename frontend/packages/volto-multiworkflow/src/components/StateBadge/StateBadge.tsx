/**
 * A small label showing one workflow's current state.
 *
 * Intended for listings, where several objects' additional states are shown at
 * a glance. It renders from either of the two shapes the backend serves:
 *
 * - a chain `entry` of the `@workflow` payload, whose titles arrive translated
 *   — the workflow's `title` being any label declared for it;
 * - a `workflow_states` `value`, which content and catalog summaries carry with
 *   no further request, but which holds ids only. Pass the translated `label`
 *   to show, such as the value's title in `WORKFLOW_STATES_VOCABULARY`; without
 *   one, the state id is shown.
 *
 * Either way the component needs no i18n of its own.
 */

import { parseWorkflowState } from '../../helpers/states';
import type { WorkflowChainEntry, WorkflowStateValue } from '../../types';

interface CommonProps {
  /** Extra class names, appended to the component's own. */
  className?: string;
}

/** Render from a chain entry of the `@workflow` payload. */
export interface EntryStateBadgeProps extends CommonProps {
  /** The chain entry to render. */
  entry: WorkflowChainEntry;
  value?: never;
  label?: never;
}

/** Render from one `workflow_states` value. */
export interface ValueStateBadgeProps extends CommonProps {
  /** A `<workflow-id>|<state-id>` value, as content and summaries carry it. */
  value: WorkflowStateValue;
  /** Translated text to show; the state id when omitted. */
  label?: string;
  entry?: never;
}

export type StateBadgeProps = EntryStateBadgeProps | ValueStateBadgeProps;

export default function StateBadge(props: StateBadgeProps) {
  const classNames = ['multiworkflow-state-badge', props.className]
    .filter(Boolean)
    .join(' ');

  if (props.entry !== undefined) {
    const { entry } = props;
    return (
      <span
        className={classNames}
        // Both are stable ids, unlike the translated titles, so they are what
        // styling and acceptance tests should key on.
        data-workflow={entry.workflow_id}
        data-state={entry.state.id}
        title={entry.title}
      >
        {entry.state.title}
      </span>
    );
  }

  const state = parseWorkflowState(props.value);
  if (state === undefined) {
    // The backend never serves such a value. Rendering nothing beats a badge
    // that names no workflow.
    return null;
  }

  return (
    <span
      className={classNames}
      data-workflow={state.workflow_id}
      data-state={state.state_id}
    >
      {props.label ?? state.state_id}
    </span>
  );
}
