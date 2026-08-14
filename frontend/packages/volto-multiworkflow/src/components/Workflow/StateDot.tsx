/**
 * The coloured dot that marks a workflow state in the select control.
 *
 * Filled for the state the object is currently in, outlined for the others.
 * Extracted from the react-select decorators so the one piece of this control
 * that is purely visual can be seen, and reviewed, on its own.
 */

import type { CSSProperties } from 'react';

export interface StateDotProps {
  /** The state's colour, as Volto's workflow helpers report it. */
  color?: string;
  /**
   * Draw the colour as an outline rather than a fill.
   *
   * Used for options that are not the object's current state.
   */
  outlined?: boolean;
}

export default function StateDot({ color, outlined = false }: StateDotProps) {
  const style: CSSProperties = {
    marginRight: '10px',
    display: 'inline-block',
    backgroundColor: outlined ? undefined : color,
    content: ' ',
    height: '10px',
    width: '10px',
    borderRadius: '50%',
    border: outlined ? `1px solid ${color}` : undefined,
  };

  return <span style={style} data-testid="workflow-state-dot" />;
}
