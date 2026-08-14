/**
 * The history table.
 *
 * Presentational: hand it processed entries and it draws them. It fetches
 * nothing, threads nothing, and decides nothing about which entries exist — the
 * container does that, so this component can be rendered from a fixture.
 *
 * The workflow column appears only when a history actually mixes workflows,
 * which is what keeps the table identical to upstream's on a site with a single
 * workflow.
 */

import { Table } from 'semantic-ui-react';
import { FormattedMessage, defineMessages, useIntl } from 'react-intl';
import type { MouseEvent } from 'react';
import type { DropdownItemProps } from 'semantic-ui-react';

import HistoryRow from './HistoryRow';
import type { HistoryEntry } from '../../types';

const messages = defineMessages({
  workflow: {
    id: 'Workflow',
    defaultMessage: 'Workflow',
  },
});

export interface HistoryTableProps {
  /** Entries, newest first, already threaded by `helpers/history`. */
  entries: HistoryEntry[];
  /** Base URL of the content object, for the diff and version links. */
  baseUrl: string;
  /**
   * Whether to render the workflow column.
   *
   * Derived by the container with `spansMultipleWorkflows`, and passed in so
   * this component stays free of that decision.
   */
  showWorkflow?: boolean;
  /** Workflow id to translated title, for the workflow column. */
  workflowTitles?: Record<string, string>;
  /** Called when the user reverts to a revision. */
  onRevert: (
    event: MouseEvent<HTMLDivElement>,
    data: DropdownItemProps,
  ) => void;
}

export default function HistoryTable({
  entries,
  baseUrl,
  showWorkflow = false,
  workflowTitles = {},
  onRevert,
}: HistoryTableProps) {
  const intl = useIntl();

  return (
    <Table selectable compact singleLine attached>
      <Table.Header>
        <Table.Row>
          <Table.HeaderCell width={1}>
            <FormattedMessage id="History Version Number" defaultMessage="#" />
          </Table.HeaderCell>
          <Table.HeaderCell width={4}>
            <FormattedMessage id="What" defaultMessage="What" />
          </Table.HeaderCell>
          {/* --- collective.multiworkflow: only when it earns its width --- */}
          {showWorkflow && (
            <Table.HeaderCell width={3}>
              {intl.formatMessage(messages.workflow)}
            </Table.HeaderCell>
          )}
          {/* --- end collective.multiworkflow --- */}
          <Table.HeaderCell width={4}>
            <FormattedMessage id="Who" defaultMessage="Who" />
          </Table.HeaderCell>
          <Table.HeaderCell width={4}>
            <FormattedMessage id="When" defaultMessage="When" />
          </Table.HeaderCell>
          <Table.HeaderCell width={4}>
            <FormattedMessage id="Change Note" defaultMessage="Change Note" />
          </Table.HeaderCell>
          <Table.HeaderCell />
        </Table.Row>
      </Table.Header>
      <Table.Body>
        {entries.map((entry) => (
          // collective.multiworkflow: the workflow id is part of the key. Two
          // workflows can record a transition in the same second and neither
          // entry carries a version, so upstream's key is not unique across a
          // merged history.
          <HistoryRow
            key={`${entry.workflow_id ?? 'versioning'}-${
              entry.version ?? entry.time
            }`}
            entry={entry}
            baseUrl={baseUrl}
            showWorkflow={showWorkflow}
            workflowTitles={workflowTitles}
            onRevert={onRevert}
          />
        ))}
      </Table.Body>
    </Table>
  );
}
