import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import StateBadge from './StateBadge';
import type { WorkflowChainEntry } from '../../types';

const entry: WorkflowChainEntry = {
  workflow_id: 'foundation_member_workflow',
  title: 'Foundation Member Workflow',
  state_variable: 'membership_state',
  state: { id: 'pending', title: 'Pending' },
  transitions: [],
  history: [],
};

describe('StateBadge', () => {
  it('shows the translated state title', () => {
    render(<StateBadge entry={entry} />);

    expect(screen.getByText('Pending')).toBeTruthy();
  });

  it('exposes stable ids as data attributes', () => {
    const { container } = render(<StateBadge entry={entry} />);
    const badge = container.querySelector('span');

    expect(badge?.getAttribute('data-workflow')).toBe(
      'foundation_member_workflow',
    );
    expect(badge?.getAttribute('data-state')).toBe('pending');
  });

  it('names the workflow in its title attribute', () => {
    const { container } = render(<StateBadge entry={entry} />);

    expect(container.querySelector('span')?.title).toBe(
      'Foundation Member Workflow',
    );
  });

  it('names the workflow by a declared label', () => {
    // The backend reports a label declared on the workflow's directive as the
    // entry's title, so the badge shows it without knowing labels exist.
    const labelled = { ...entry, title: 'Foundation membership' };
    const { container } = render(<StateBadge entry={labelled} />);

    expect(container.querySelector('span')?.title).toBe(
      'Foundation membership',
    );
  });

  it('appends extra class names to its own', () => {
    const { container } = render(<StateBadge entry={entry} className="mine" />);

    expect(container.querySelector('span')?.className).toBe(
      'multiworkflow-state-badge mine',
    );
  });

  it('keeps its own class when none is passed', () => {
    const { container } = render(<StateBadge entry={entry} />);

    expect(container.querySelector('span')?.className).toBe(
      'multiworkflow-state-badge',
    );
  });
});

describe('StateBadge from a workflow_states value', () => {
  const value = 'foundation_member_workflow|pending';

  it('shows the label it is given', () => {
    const { container } = render(
      <StateBadge value={value} label="Membership: Pending" />,
    );

    expect(container.querySelector('span')?.textContent).toBe(
      'Membership: Pending',
    );
  });

  it('falls back to the state id without a label', () => {
    const { container } = render(<StateBadge value={value} />);

    expect(container.querySelector('span')?.textContent).toBe('pending');
  });

  it('exposes the ids it parses as data attributes', () => {
    const { container } = render(<StateBadge value={value} />);
    const badge = container.querySelector('span');

    expect(badge?.getAttribute('data-workflow')).toBe(
      'foundation_member_workflow',
    );
    expect(badge?.getAttribute('data-state')).toBe('pending');
  });

  it('sets no title attribute, having no workflow title to put there', () => {
    const { container } = render(<StateBadge value={value} />);

    expect(container.querySelector('span')?.hasAttribute('title')).toBe(false);
  });

  it('appends extra class names to its own', () => {
    const { container } = render(<StateBadge value={value} className="mine" />);

    expect(container.querySelector('span')?.className).toBe(
      'multiworkflow-state-badge mine',
    );
  });

  it('renders nothing for a value naming no workflow', () => {
    const { container } = render(<StateBadge value="pending" />);

    expect(container.firstChild).toBeNull();
  });
});
