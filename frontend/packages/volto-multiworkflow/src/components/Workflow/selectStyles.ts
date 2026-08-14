/**
 * react-select theme and styles for the workflow control.
 *
 * Copied verbatim from `@plone/volto`'s Workflow component so the control keeps
 * looking exactly like the one it shadows. Configuration only: nothing here
 * renders, so nothing here has a story.
 */

import type { SelectTheme } from './types';

type Styles = Record<string, unknown>;

export const selectTheme = (theme: SelectTheme): SelectTheme => ({
  ...theme,
  borderRadius: 0,
  colors: {
    ...theme.colors,
    primary25: 'hotpink',
    primary: '#b8c6c8',
  },
});

export const customSelectStyles = {
  control: (styles: Styles, state: { menuIsOpen: boolean }) => ({
    ...styles,
    border: 'none',
    borderBottom: '2px solid #b8c6c8',
    boxShadow: 'none',
    borderBottomStyle: state.menuIsOpen ? 'dotted' : 'solid',
  }),
  menu: (styles: Styles) => ({
    ...styles,
    top: null,
    marginTop: 0,
    boxShadow: 'none',
    borderBottom: '2px solid #b8c6c8',
  }),
  indicatorSeparator: (styles: Styles) => ({
    ...styles,
    width: null,
  }),
  valueContainer: (styles: Styles) => ({
    ...styles,
    padding: 0,
  }),
  option: (
    styles: Styles,
    state: { isSelected: boolean; isFocused: boolean },
  ) => ({
    ...styles,
    backgroundColor: null,
    minHeight: '50px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 12px',
    color: state.isSelected
      ? '#007bc1'
      : state.isFocused
        ? '#4a4a4a'
        : 'inherit',
    ':active': {
      backgroundColor: null,
    },
    span: {
      flex: '0 0 auto',
    },
    svg: {
      flex: '0 0 auto',
    },
  }),
};
