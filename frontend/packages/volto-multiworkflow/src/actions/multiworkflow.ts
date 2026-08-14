/**
 * Redux actions for additional workflows.
 *
 * Volto core's own workflow reducer keeps only `state`, `history` and
 * `transitions` from the `@workflow` response and discards everything else,
 * so the `chain` key never reaches the store. These actions exist to carry it.
 */

import { flattenToAppURL } from '@plone/volto/helpers/Url/Url';

export const GET_MULTIWORKFLOW = 'GET_MULTIWORKFLOW';
export const TRANSITION_MULTIWORKFLOW = 'TRANSITION_MULTIWORKFLOW';

/**
 * Fetch the full `@workflow` payload, including the `chain` key.
 *
 * @param url Content object URL.
 */
export function getMultiWorkflow(url: string) {
  return {
    type: GET_MULTIWORKFLOW,
    request: { op: 'get', path: `${flattenToAppURL(url)}/@workflow` },
  };
}

/**
 * Execute a transition by posting to its `@id`.
 *
 * The `@id` is an absolute backend URL, so it has to be flattened before it
 * reaches the API client — exactly as core's own `transitionWorkflow` does.
 *
 * Note the response is *not* a workflow payload: plone.restapi replies with the
 * last `review_history` entry, so the chain has to be re-fetched afterwards.
 *
 * @param transitionUrl The transition's `@id` from the payload.
 */
export function transitionMultiWorkflow(transitionUrl: string) {
  return {
    type: TRANSITION_MULTIWORKFLOW,
    request: { op: 'post', path: flattenToAppURL(transitionUrl), data: {} },
  };
}
