/**
 * The contents of one option row in the workflow select.
 *
 * A dot, the label, and a check mark whose colour says whether the row is the
 * selected one or merely the focused one. Split out of `Option` so that the
 * whole visual vocabulary of the control can be rendered without react-select,
 * and therefore reviewed in Storybook.
 */

import Icon from '@plone/volto/components/theme/Icon/Icon';
import checkSVG from '@plone/volto/icons/check.svg';
import StateDot from './StateDot';

export interface OptionLabelProps {
  /** The option's label, already translated by the backend. */
  label?: string;
  /** The option's state colour. */
  color?: string;
  /** Whether this option is the object's current state. */
  isCurrent?: boolean;
  /** Whether react-select reports this option as selected. */
  isSelected?: boolean;
  /** Whether react-select reports this option as focused. */
  isFocused?: boolean;
}

export default function OptionLabel({
  label,
  color,
  isCurrent = false,
  isSelected = false,
  isFocused = false,
}: OptionLabelProps) {
  return (
    <>
      <StateDot color={color} outlined={!isCurrent} />
      <div style={{ marginRight: 'auto' }}>{label}</div>
      {isFocused && !isSelected && (
        <Icon name={checkSVG} size="18px" color="#b8c6c8" />
      )}
      {isSelected && <Icon name={checkSVG} size="18px" color="#007bc1" />}
    </>
  );
}
