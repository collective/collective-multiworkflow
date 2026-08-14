/**
 * `HistoryTable` renders a merged history.
 *
 * These stories are the clearest statement of what this add-on changes about
 * the history view — compare `SingleWorkflow` with `MergedWorkflows`.
 */

import HistoryTable from './HistoryTable';
import type { HistoryTableProps } from './HistoryTable';
import {
  mergedHistory,
  singleWorkflowHistory,
  workflowTitles,
} from '../../stories/fixtures';
import { withStore } from '../../stories/withStore';
import type { Story, StoryMeta } from '../../stories/csf';

const meta: StoryMeta<HistoryTableProps> = {
  title: 'Multiworkflow/History/HistoryTable',
  component: HistoryTable,
  args: {
    baseUrl: '/doc',
    onRevert: () => {
      // eslint-disable-next-line no-console
      console.log('revert');
    },
  },
  // Volto's FormattedDate reads the locale from the store.
  decorators: [withStore()],
  parameters: {
    docs: {
      description: {
        component:
          'Presentational: it is handed entries that have already been ' +
          'threaded per workflow by `helpers/history`, and draws them. It ' +
          'fetches nothing and decides nothing about which entries exist.',
      },
    },
  },
};

export default meta;

/**
 * A site without this add-on: one workflow, and no workflow column.
 *
 * This is the table Plone has always shown, and the add-on must not change it.
 */
export const SingleWorkflow: Story<HistoryTableProps> = {
  args: {
    entries: singleWorkflowHistory,
    showWorkflow: false,
    workflowTitles,
  },
};

/**
 * A merged history: two workflows plus versioning entries.
 *
 * Read the *What* column down the page. Each transition shows the state its
 * own workflow came from, so `Pending → Active` sits next to
 * `Private → Published` without either borrowing the other's state.
 */
export const MergedWorkflows: Story<HistoryTableProps> = {
  args: {
    entries: mergedHistory,
    showWorkflow: true,
    workflowTitles,
  },
};

/**
 * The same entries without the titles the chain would supply.
 *
 * The column falls back to the raw workflow id, which is what happens when the
 * `@workflow` payload has not loaded yet.
 */
export const WithoutWorkflowTitles: Story<HistoryTableProps> = {
  args: {
    entries: mergedHistory,
    showWorkflow: true,
    workflowTitles: {},
  },
};

/** Nothing recorded yet: headers only. */
export const Empty: Story<HistoryTableProps> = {
  args: { entries: [], showWorkflow: false, workflowTitles },
};
