/**
 * One labelled state selector.
 *
 * The publication workflow and every additional one render through this, so
 * the two differ in the props they pass and nowhere else. Extracted from the
 * two nearly identical blocks the container used to carry.
 *
 * Presentational, but react-select arrives through `injectLazyLibs` further up,
 * so `Select` and `Placeholder` are passed in rather than imported. That also
 * means this component cannot be rendered in Storybook without stubbing the
 * library, which is why the visual pieces it composes — `StateDot` and
 * `OptionLabel` — carry the stories instead.
 */

import uniqBy from 'lodash/uniqBy';
import { FormFieldWrapper as VoltoFormFieldWrapper } from '@plone/volto/components/manage/Widgets';
import { getWorkflowOptions } from '@plone/volto/helpers/Workflows/Workflows';
import type { ComponentType, ReactNode } from 'react';
import DropdownIndicator from './DropdownIndicator';
import Option from './Option';
import SingleValue from './SingleValue';
import { customSelectStyles, selectTheme } from './selectStyles';
import type { SelectRenderProps, WorkflowOption } from './types';
import type { WorkflowTransition } from '../../types';

/**
 * `FormFieldWrapper` is a loadable wrapper around a JS component, so its
 * generated props type is `Object` — it accepts no `children` and no spread.
 * Re-typing it here keeps the JSX identical to upstream's, which is what makes
 * re-applying a Volto upgrade a small diff.
 */
const FormFieldWrapper = VoltoFormFieldWrapper as ComponentType<
  Record<string, unknown> & { children?: ReactNode }
>;

export interface WorkflowSelectProps {
  /** Field id; also the select's name. */
  id: string;
  /** Label shown above the control. */
  title: string;
  /** Transitions available to the current user, in payload order. */
  transitions: WorkflowTransition[];
  /** The option describing the state the object is in. */
  value: WorkflowOption;
  /** Whether the control accepts input. */
  isDisabled?: boolean;
  /** Called with the chosen option. */
  onChange: (option: WorkflowOption) => void;
  /** react-select itself, injected by the container. */
  Select: ComponentType<Record<string, unknown>>;
  /** react-select's `Placeholder`, injected by the container. */
  Placeholder: ComponentType<SelectRenderProps>;
  /** Passed through to `FormFieldWrapper`, as upstream does. */
  [key: string]: unknown;
}

export default function WorkflowSelect({
  id,
  title,
  transitions,
  value,
  isDisabled = false,
  onChange,
  Select,
  Placeholder,
  ...props
}: WorkflowSelectProps) {
  return (
    <FormFieldWrapper id={id} title={title} {...props}>
      <Select
        name={id}
        className="react-select-container"
        classNamePrefix="react-select"
        isDisabled={isDisabled}
        // The current state is appended as an option so the control has
        // something to display; `uniqBy` drops a transition that would repeat
        // a label already offered.
        options={uniqBy(
          transitions.map((transition) => getWorkflowOptions(transition)),
          'label',
        ).concat(value)}
        styles={customSelectStyles}
        theme={selectTheme}
        components={{
          DropdownIndicator,
          Placeholder,
          Option,
          SingleValue,
        }}
        onChange={onChange}
        value={value}
        isSearchable={false}
      />
    </FormFieldWrapper>
  );
}
