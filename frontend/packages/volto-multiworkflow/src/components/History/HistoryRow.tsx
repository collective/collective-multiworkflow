/**
 * One row of the history table.
 *
 * Presentational: it is handed a processed entry and draws it. The threading
 * that gives an entry its `prev_state_title`, and the decision to show the
 * workflow column at all, both happen before this component sees anything —
 * see `helpers/history`.
 */

import { Link } from 'react-router-dom';
import { Dropdown, Icon, Table } from 'semantic-ui-react';
import { FormattedMessage } from 'react-intl';
import type { ComponentType, MouseEvent } from 'react';
import type { DropdownItemProps } from 'semantic-ui-react';

import VoltoFormattedDate from '@plone/volto/components/theme/FormattedDate/FormattedDate';
import type { HistoryEntry } from '../../types';

/**
 * `FormattedDate` is a loadable wrapper around a JS component, so its
 * generated props type demands every prop the implementation destructures.
 * Re-typing it here keeps the JSX below identical to upstream's, which is what
 * makes re-applying a Volto upgrade a small diff.
 */
const FormattedDate = VoltoFormattedDate as unknown as ComponentType<{
  date: string;
  [key: string]: unknown;
}>;

export interface HistoryRowProps {
  /** One entry of the processed history. */
  entry: HistoryEntry;
  /** Base URL of the content object, for the diff and version links. */
  baseUrl: string;
  /** Whether to render the workflow column. */
  showWorkflow: boolean;
  /** Workflow id to translated title, for the workflow column. */
  workflowTitles: Record<string, string>;
  /** Called when the user reverts to a revision. */
  onRevert: (
    event: MouseEvent<HTMLDivElement>,
    data: DropdownItemProps,
  ) => void;
}

export default function HistoryRow({
  entry,
  baseUrl,
  showWorkflow,
  workflowTitles,
  onRevert,
}: HistoryRowProps) {
  const hasVersion = 'version' in entry && (entry.version as number) > 0;
  const diffUrl = `${baseUrl}/diff?one=${
    (entry.version as number) - 1
  }&two=${entry.version}`;

  return (
    <Table.Row>
      <Table.Cell>
        {(hasVersion && (
          <Link className="item" to={diffUrl}>
            {entry.version}
          </Link>
        )) || <span>{entry.version}</span>}
      </Table.Cell>
      <Table.Cell>
        {(hasVersion && (
          <Link className="item" to={diffUrl}>
            {entry.transition_title}
          </Link>
        )) || (
          <span>
            {entry.transition_title}
            {entry.type === 'workflow' &&
              ` (${entry.action ? `${entry.prev_state_title} → ` : ''}${
                entry.state_title
              })`}
          </span>
        )}
      </Table.Cell>
      {/* --- collective.multiworkflow: which workflow recorded this --- */}
      {showWorkflow && (
        <Table.Cell data-workflow={entry.workflow_id ?? ''}>
          {entry.workflow_id
            ? workflowTitles[entry.workflow_id] ?? entry.workflow_id
            : ''}
        </Table.Cell>
      )}
      {/* --- end collective.multiworkflow --- */}
      <Table.Cell>{entry.actor.fullname}</Table.Cell>
      <Table.Cell>
        <FormattedDate date={entry.time} />
      </Table.Cell>
      <Table.Cell>{entry.comments}</Table.Cell>
      <Table.Cell>
        {entry.type === 'versioning' && (
          <Dropdown icon="ellipsis horizontal">
            <Dropdown.Menu className="left">
              {hasVersion && (
                <Link className="item" to={diffUrl}>
                  <Icon name="copy" />{' '}
                  <FormattedMessage
                    id="View changes"
                    defaultMessage="View changes"
                  />
                </Link>
              )}
              {'version' in entry && (
                <Link
                  className="item"
                  to={`${baseUrl}?version=${entry.version}`}
                >
                  <Icon name="eye" />{' '}
                  <FormattedMessage
                    id="View this revision"
                    defaultMessage="View this revision"
                  />
                </Link>
              )}
              {'version' in entry && entry.may_revert && !entry.is_current && (
                <Dropdown.Item value={entry.version} onClick={onRevert}>
                  <Icon name="undo" />{' '}
                  <FormattedMessage
                    id="Revert to this revision"
                    defaultMessage="Revert to this revision"
                  />
                </Dropdown.Item>
              )}
            </Dropdown.Menu>
          </Dropdown>
        )}
      </Table.Cell>
    </Table.Row>
  );
}
