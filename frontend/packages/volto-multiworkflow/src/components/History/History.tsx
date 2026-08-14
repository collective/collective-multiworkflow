/**
 * The history view, made safe for a chain of workflows.
 *
 * A TypeScript port of `@plone/volto`'s `components/manage/History/History`,
 * with three added blocks marked `--- collective.multiworkflow ---`. Kept
 * close to upstream so a Volto upgrade stays a small diff: re-read the
 * original and re-apply those blocks.
 *
 * What changes. Upstream derives each entry's previous state from the entry
 * *before it in the list*, which holds only while a history describes one
 * workflow. `@history` merges every workflow in the chain into one stream, so
 * the preceding entry usually belongs to a different workflow and the derived
 * arrows become fiction — `Published → Active` between two workflows that
 * never interacted. The threading is therefore done per `workflow_id`, and
 * when a history does span several workflows each row says which one it came
 * from.
 *
 * With a single workflow — every object on a site without this add-on — the
 * threading reduces to upstream's, the extra column is not rendered, and the
 * table is exactly the one Plone has always shown.
 *
 * This file is the container: permissions, fetching, threading, and the
 * toolbar. The table itself is `HistoryTable`, which takes the processed
 * entries and nothing else.
 */

import { useEffect, useMemo, useCallback } from 'react';
import Helmet from '@plone/volto/helpers/Helmet/Helmet';
import { Link, useLocation } from 'react-router-dom';
import { useDispatch, useSelector, shallowEqual } from 'react-redux';
import { compose } from 'redux';
import { Container as SemanticContainer, Segment } from 'semantic-ui-react';
import type { MouseEvent } from 'react';
import type { DropdownItemProps } from 'semantic-ui-react';
import find from 'lodash/find';
import { createPortal } from 'react-dom';
import { FormattedMessage, defineMessages, useIntl } from 'react-intl';
import { asyncConnect } from '@plone/volto/helpers/AsyncConnect';

import IconNext from '@plone/volto/components/theme/Icon/Icon';
import Toolbar from '@plone/volto/components/manage/Toolbar/Toolbar';
import Forbidden from '@plone/volto/components/theme/Forbidden/Forbidden';
import Unauthorized from '@plone/volto/components/theme/Unauthorized/Unauthorized';
import {
  getHistory,
  revertHistory,
} from '@plone/volto/actions/history/history';
import { listActions } from '@plone/volto/actions/actions/actions';
import { getBaseUrl } from '@plone/volto/helpers/Url/Url';
import { useClient } from '@plone/volto/hooks/client/useClient';
import config from '@plone/volto/registry';

import backSVG from '@plone/volto/icons/back.svg';

import HistoryTable from './HistoryTable';

// --- collective.multiworkflow (1/3): imports ---
import { getMultiWorkflow } from '@plone-collective/volto-multiworkflow/actions/multiworkflow';
import {
  getWorkflowTitles,
  markCurrentVersion,
  spansMultipleWorkflows,
  threadPreviousStates,
} from '@plone-collective/volto-multiworkflow/helpers/history';
import type {
  HistoryEntry,
  MultiWorkflowState,
} from '@plone-collective/volto-multiworkflow/types';
// --- end collective.multiworkflow ---

/** An entry of `state.actions.actions.object`. */
interface ObjectAction {
  id: string;
  [key: string]: unknown;
}

/** The slice of the store this view reads. */
interface StoreShape {
  actions: { actions: { object?: ObjectAction[] } };
  userSession: { token?: string | null };
  history: { entries: HistoryEntry[] };
  content: { data?: { title?: string } };
  multiworkflow?: MultiWorkflowState;
}

export interface HistoryProps {
  /** Passed through to the Forbidden/Unauthorized views during SSR. */
  staticContext?: unknown;
}

const messages = defineMessages({
  back: {
    id: 'Back',
    defaultMessage: 'Back',
  },
  history: {
    id: 'History',
    defaultMessage: 'History',
  },
});

const History = (props: HistoryProps) => {
  const { staticContext } = props;
  const isClient = useClient();
  const dispatch = useDispatch();
  const location = useLocation();
  const pathname = location.pathname;
  const intl = useIntl();

  const objectActions = useSelector(
    (state: StoreShape) => state.actions.actions.object,
  );
  const token = useSelector((state: StoreShape) => state.userSession.token);
  const entries = useSelector((state: StoreShape) => state.history.entries);
  const title = useSelector((state: StoreShape) => state.content.data?.title);

  // --- collective.multiworkflow (2a/3): the chain, for workflow titles ---
  // History entries name their workflow by id only; the titles live on the
  // `@workflow` payload, so the view reads both.
  const chain = useSelector(
    (state: StoreShape) => state.multiworkflow?.chain ?? [],
    shallowEqual,
  );
  const workflowTitles = useMemo(() => getWorkflowTitles(chain), [chain]);
  // --- end collective.multiworkflow ---

  const onRevert = useCallback(
    (event: MouseEvent<HTMLDivElement>, { value }: DropdownItemProps) => {
      const baseUrl = getBaseUrl(pathname);
      // `dispatch` is typed as returning the action, so the thenable the API
      // middleware actually hands back has to be re-wrapped.
      Promise.resolve(
        dispatch(revertHistory(baseUrl, value as number) as never),
      ).then(() => {
        dispatch(getHistory(baseUrl) as never);
      });
    },
    [dispatch, pathname],
  );

  useEffect(() => {
    dispatch(getHistory(getBaseUrl(pathname)) as never);
    // collective.multiworkflow: read the chain alongside core's history.
    dispatch(getMultiWorkflow(getBaseUrl(pathname)) as never);
  }, [dispatch, pathname]);

  // --- collective.multiworkflow (2b/3): thread states per workflow ---
  // Upstream walks the list once, carrying the previous entry's state title
  // forward regardless of which workflow recorded it. Both helpers below
  // return new objects instead of annotating the store's.
  const processedEntries = useMemo(
    () => markCurrentVersion(threadPreviousStates(entries)),
    [entries],
  );
  const showWorkflow = useMemo(
    () => spansMultipleWorkflows(processedEntries),
    [processedEntries],
  );
  // --- end collective.multiworkflow ---

  const historyAction = find(objectActions, {
    id: 'history',
  });

  const Container =
    config.getComponent({ name: 'Container' }).component || SemanticContainer;

  return !historyAction ? (
    <>
      {token ? (
        <Forbidden pathname={pathname} staticContext={staticContext} />
      ) : (
        <Unauthorized pathname={pathname} staticContext={staticContext} />
      )}
    </>
  ) : (
    <Container id="page-history">
      <Helmet title={intl.formatMessage(messages.history)} />
      <Segment.Group raised>
        <Segment className="primary">
          <FormattedMessage
            id="History of {title}"
            defaultMessage="History of {title}"
            values={{
              title: <q>{title}</q>,
            }}
          />
        </Segment>
        <Segment secondary>
          <FormattedMessage
            id="You can view the history of your item below."
            defaultMessage="You can view the history of your item below."
          />
        </Segment>
        {/* --- collective.multiworkflow (3/3): the table is handed processed
            entries and the workflow column's inputs --- */}
        <HistoryTable
          entries={processedEntries}
          baseUrl={getBaseUrl(pathname)}
          showWorkflow={showWorkflow}
          workflowTitles={workflowTitles}
          onRevert={onRevert}
        />
        {/* --- end collective.multiworkflow --- */}
      </Segment.Group>
      {isClient &&
        createPortal(
          <Toolbar
            pathname={pathname}
            hideDefaultViewButtons
            inner={
              <Link to={`${getBaseUrl(pathname)}`} className="item">
                <IconNext
                  name={backSVG}
                  className="contents circled"
                  size="30px"
                  title={intl.formatMessage(messages.back)}
                />
              </Link>
            }
          />,
          document.getElementById('toolbar') as HTMLElement,
        )}
    </Container>
  );
};

export default compose(
  asyncConnect([
    {
      key: 'actions',
      promise: async ({
        location,
        store: { dispatch },
      }: {
        location: { pathname: string };
        store: { dispatch: (action: unknown) => Promise<unknown> };
      }) => await dispatch(listActions(getBaseUrl(location.pathname))),
    },
  ]),
)(History);
