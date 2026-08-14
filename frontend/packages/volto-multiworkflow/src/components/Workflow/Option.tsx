/**
 * react-select's `Option`, rendering one workflow state.
 *
 * Glue: the row's contents are `OptionLabel`, and the surrounding component is
 * react-select's own, reached through `injectLazyLibs`. That lazy injection is
 * why this file has no story — `OptionLabel` carries one instead.
 */

import { injectLazyLibs } from '@plone/volto/helpers/Loadable/Loadable';
import OptionLabel from './OptionLabel';
import type { SelectRenderProps } from './types';

const Option = injectLazyLibs('reactSelect')((props: SelectRenderProps) => {
  const isCurrent = props.selectProps.value?.value === props.data?.value;
  const { Option } = props.reactSelect.components;

  return (
    <Option {...props}>
      <OptionLabel
        label={props.label}
        // The current option is filled with the *selected* value's colour, as
        // upstream does; every other option is outlined with its own.
        color={isCurrent ? props.selectProps.value?.color : props.data?.color}
        isCurrent={isCurrent}
        isSelected={props.isSelected}
        isFocused={props.isFocused}
      />
    </Option>
  );
});

export default Option;
