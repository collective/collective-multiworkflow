/**
 * A small label showing one workflow's current state.
 *
 * Intended for listings, where several objects' additional states are shown at
 * a glance. Titles arrive already translated from the backend serializer, so
 * this component needs no i18n of its own.
 */

import type { WorkflowChainEntry } from '../../types';

export interface StateBadgeProps {
  /** The chain entry to render. */
  entry: WorkflowChainEntry;
  /** Extra class names, appended to the component's own. */
  className?: string;
}

export default function StateBadge({ entry, className }: StateBadgeProps) {
  const classNames = ['multiworkflow-state-badge', className]
    .filter(Boolean)
    .join(' ');

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
