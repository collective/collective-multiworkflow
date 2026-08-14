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
