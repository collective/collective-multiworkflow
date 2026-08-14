/**
 * react-select's `DropdownIndicator`, as a chevron that follows the menu.
 *
 * Glue, like its two siblings: the only logic is which icon the open state
 * calls for, and the surrounding component comes from `injectLazyLibs`.
 */

import { injectLazyLibs } from '@plone/volto/helpers/Loadable/Loadable';
import Icon from '@plone/volto/components/theme/Icon/Icon';
import downSVG from '@plone/volto/icons/down-key.svg';
import upSVG from '@plone/volto/icons/up-key.svg';
import type { SelectRenderProps } from './types';

const DropdownIndicator = injectLazyLibs('reactSelect')((
  props: SelectRenderProps,
) => {
  const { DropdownIndicator } = props.reactSelect.components;
  return (
    <DropdownIndicator {...props} data-testid="workflow-select-dropdown">
      <Icon
        name={props.selectProps.menuIsOpen ? upSVG : downSVG}
        size="24px"
        color="#007bc1"
      />
    </DropdownIndicator>
  );
});

export default DropdownIndicator;
