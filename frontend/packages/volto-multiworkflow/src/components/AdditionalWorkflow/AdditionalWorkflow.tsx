/**
 * Store-connected wrapper around `AdditionalWorkflowMenu`.
 *
 * Fetches the full `@workflow` payload for a content object, and re-fetches
 * after a transition: plone.restapi's transition endpoint answers with the last
 * `review_history` entry rather than the workflow payload, so the new states
 * can only be learned by asking again.
 */

import { useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getContent } from '@plone/volto/actions/content/content';
import {
  getMultiWorkflow,
  transitionMultiWorkflow,
} from '../../actions/multiworkflow';
import AdditionalWorkflowMenu from '../AdditionalWorkflowMenu/AdditionalWorkflowMenu';
import type { MultiWorkflowState } from '../../types';

export interface AdditionalWorkflowProps {
  /** URL of the content object whose workflows are shown. */
  url: string;
}

interface StoreShape {
  multiworkflow?: MultiWorkflowState;
}

export default function AdditionalWorkflow({ url }: AdditionalWorkflowProps) {
  const dispatch = useDispatch();
  const chain = useSelector(
    (state: StoreShape) => state.multiworkflow?.chain ?? [],
  );
  const loading = useSelector(
    (state: StoreShape) => state.multiworkflow?.loading ?? false,
  );

  useEffect(() => {
    dispatch(getMultiWorkflow(url) as never);
  }, [dispatch, url]);

  const onTransition = useCallback(
    (transitionUrl: string) => {
      Promise.resolve(
        dispatch(transitionMultiWorkflow(transitionUrl) as never),
      ).then(() => {
        dispatch(getMultiWorkflow(url) as never);
        // An additional workflow's transition can change indexed values, so let the rest of
        // the UI see the updated object too.
        dispatch(getContent(url) as never);
      });
    },
    [dispatch, url],
  );

  return (
    <AdditionalWorkflowMenu
      chain={chain}
      onTransition={onTransition}
      disabled={loading}
    />
  );
}
