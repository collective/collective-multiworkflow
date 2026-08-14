import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import AdditionalWorkflowMenu from './AdditionalWorkflowMenu';
import type { WorkflowChainEntry } from '../../types';

const publication: WorkflowChainEntry = {
  workflow_id: 'simple_publication_workflow',
  title: 'Simple Publication Workflow',
  state_variable: 'review_state',
  state: { id: 'private', title: 'Private' },
  transitions: [{ '@id': 'http://x/@workflow/publish', title: 'Publish' }],
  history: [],
};

const membership: WorkflowChainEntry = {
  workflow_id: 'foundation_member_workflow',
  title: 'Foundation Member Workflow',
  state_variable: 'membership_state',
  state: { id: 'pending', title: 'Pending' },
  transitions: [{ '@id': 'http://x/@workflow/activate', title: 'Activate' }],
  history: [],
};

describe('AdditionalWorkflowMenu', () => {
  it('renders nothing without a chain', () => {
    const { container } = render(
      <AdditionalWorkflowMenu onTransition={vi.fn()} />,
    );

    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when only the publication workflow is present', () => {
    const { container } = render(
      <AdditionalWorkflowMenu chain={[publication]} onTransition={vi.fn()} />,
    );

    expect(container.firstChild).toBeNull();
  });

  it('shows the additional workflow and its state', () => {
    render(
      <AdditionalWorkflowMenu
        chain={[publication, membership]}
        onTransition={vi.fn()}
      />,
    );

    expect(screen.getByText('Foundation Member Workflow')).toBeTruthy();
    expect(screen.getByText('Pending')).toBeTruthy();
  });

  it('does not show the publication workflow', () => {
    render(
      <AdditionalWorkflowMenu
        chain={[publication, membership]}
        onTransition={vi.fn()}
      />,
    );

    expect(screen.queryByText('Simple Publication Workflow')).toBeNull();
    expect(screen.queryByText('Publish')).toBeNull();
  });

  it('calls back with the transition url', async () => {
    const onTransition = vi.fn();
    render(
      <AdditionalWorkflowMenu
        chain={[publication, membership]}
        onTransition={onTransition}
      />,
    );

    screen.getByRole('button', { name: 'Activate' }).click();

    expect(onTransition).toHaveBeenCalledWith('http://x/@workflow/activate');
  });

  it('disables the transitions while busy', () => {
    render(
      <AdditionalWorkflowMenu
        chain={[publication, membership]}
        onTransition={vi.fn()}
        disabled
      />,
    );

    const button = screen.getByRole('button', {
      name: 'Activate',
    }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
  });

  it('renders a workflow with no available transitions', () => {
    render(
      <AdditionalWorkflowMenu
        chain={[publication, { ...membership, transitions: [] }]}
        onTransition={vi.fn()}
      />,
    );

    expect(screen.getByText('Pending')).toBeTruthy();
    expect(screen.queryByRole('button')).toBeNull();
  });

  it('renders every additional workflow', () => {
    const review: WorkflowChainEntry = {
      ...membership,
      workflow_id: 'peer_review_workflow',
      title: 'Peer Review Workflow',
      state: { id: 'unreviewed', title: 'Unreviewed' },
      transitions: [],
    };

    render(
      <AdditionalWorkflowMenu
        chain={[publication, membership, review]}
        onTransition={vi.fn()}
      />,
    );

    expect(screen.getByText('Foundation Member Workflow')).toBeTruthy();
    expect(screen.getByText('Peer Review Workflow')).toBeTruthy();
  });
});
