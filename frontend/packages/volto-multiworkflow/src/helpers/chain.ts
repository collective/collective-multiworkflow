/**
 * Helpers for reading a workflow chain.
 *
 * The chain is always ordered: the type's configured workflow comes first and
 * contributed workflows follow, because the backend adapter only ever appends.
 * Everything here relies on that ordering.
 */

import type { WorkflowChainEntry } from '../types';

/**
 * The primary workflow — the one driving `review_state`.
 *
 * @param chain The `chain` key of the `@workflow` payload.
 * @returns The first entry, or `undefined` when the chain is empty or absent.
 */
export function getPrimaryWorkflow(
  chain?: WorkflowChainEntry[],
): WorkflowChainEntry | undefined {
  return chain?.[0];
}

/**
 * The additional workflows, i.e. everything the add-on contributed.
 *
 * @param chain The `chain` key of the `@workflow` payload.
 * @returns Entries after the first; empty when there are none, which is the
 *   case for all content that does not use this add-on.
 */
export function getAdditionalWorkflows(
  chain?: WorkflowChainEntry[],
): WorkflowChainEntry[] {
  return chain?.slice(1) ?? [];
}

/**
 * Whether an object has any additional workflow worth rendering.
 *
 * @param chain The `chain` key of the `@workflow` payload.
 */
export function hasAdditionalWorkflows(chain?: WorkflowChainEntry[]): boolean {
  return getAdditionalWorkflows(chain).length > 0;
}
