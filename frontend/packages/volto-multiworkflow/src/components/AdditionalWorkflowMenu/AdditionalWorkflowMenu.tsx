/**
 * Renders each additional workflow's state and available transitions.
 *
 * Presentational on purpose: it takes the chain and a callback, so it can be
 * tested without a store and reused wherever the payload is available.
 */

import { getAdditionalWorkflows } from '../../helpers/chain';
import StateBadge from '../StateBadge/StateBadge';
import type { WorkflowChainEntry } from '../../types';

export interface AdditionalWorkflowMenuProps {
  /** The `chain` key of the `@workflow` payload; may be absent. */
  chain?: WorkflowChainEntry[];
  /** Called with a transition's `@id` when the user picks it. */
  onTransition: (transitionUrl: string) => void;
  /** Disables the transition buttons, e.g. while a request is in flight. */
  disabled?: boolean;
}

export default function AdditionalWorkflowMenu({
  chain,
  onTransition,
  disabled = false,
}: AdditionalWorkflowMenuProps) {
  const workflows = getAdditionalWorkflows(chain);

  // Content without additional workflows renders nothing at all, so the add-on
  // is invisible on a vanilla site.
  if (workflows.length === 0) {
    return null;
  }

  return (
    <div className="multiworkflow-menu">
      {workflows.map((entry) => (
        <section
          key={entry.workflow_id}
          className="multiworkflow-menu-workflow"
          data-workflow={entry.workflow_id}
        >
          <h3 className="multiworkflow-menu-title">{entry.title}</h3>
          <StateBadge entry={entry} />
          {entry.transitions.length > 0 && (
            <ul className="multiworkflow-menu-transitions">
              {entry.transitions.map((transition) => (
                <li key={transition['@id']}>
                  <button
                    type="button"
                    disabled={disabled}
                    onClick={() => onTransition(transition['@id'])}
                  >
                    {transition.title}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      ))}
    </div>
  );
}
