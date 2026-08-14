/**
 * react-select's `SingleValue`, with the current state's dot in front of it.
 *
 * Glue: everything visual lives in `StateDot`, and everything else is
 * react-select's own component reached through `injectLazyLibs`. That lazy
 * injection is why this file has no story — it renders nothing without the
 * loadable provider.
 */

import { injectLazyLibs } from '@plone/volto/helpers/Loadable/Loadable';
import StateDot from './StateDot';
import type { SelectRenderProps } from './types';

const SingleValue = injectLazyLibs('reactSelect')(({
  children,
  ...props
}: SelectRenderProps) => {
  const { SingleValue } = props.reactSelect.components;
  return (
    <SingleValue {...props}>
      <StateDot color={props.selectProps.value?.color} />
      {children}
    </SingleValue>
  );
});

export default SingleValue;
