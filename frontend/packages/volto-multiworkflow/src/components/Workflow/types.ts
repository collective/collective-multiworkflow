/**
 * Types shared by the workflow control and its react-select decorators.
 *
 * Kept in their own module so the decorators can be split into one file each
 * without importing from the container that uses them.
 */

import type { ComponentType, ReactNode } from 'react';

/**
 * A react-select option, as produced by Volto's workflow helpers.
 *
 * `url` is present on transition options and absent on the current-state one,
 * which is why the change handlers accept it as optional.
 */
export interface WorkflowOption {
  label: string;
  value: string;
  color?: string;
  url?: string;
}

/** The subset of react-select's render props these decorators touch. */
export interface SelectRenderProps {
  children?: ReactNode;
  label?: string;
  data?: WorkflowOption;
  isFocused?: boolean;
  isSelected?: boolean;
  selectProps: { value?: WorkflowOption; menuIsOpen?: boolean };
  /** Injected by `injectLazyLibs('reactSelect')`. */
  reactSelect: {
    default: ComponentType<Record<string, unknown>>;
    components: Record<string, ComponentType<SelectRenderProps>>;
  };
}

export interface SelectTheme {
  colors: Record<string, string>;
  [key: string]: unknown;
}
