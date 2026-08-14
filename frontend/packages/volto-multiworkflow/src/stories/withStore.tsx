/**
 * A Storybook decorator supplying a read-only Redux store.
 *
 * Several components below the ones this add-on ships read from the store even
 * when they take everything they draw as props: Volto's `FormattedDate` reads
 * `state.intl.locale`, for instance. Rather than stub those components, the
 * stories hand them a store with just enough state in it.
 *
 * The store never changes: `dispatch` returns the action and notifies nobody,
 * which is what a story wants — the rendered output stays the one the fixture
 * describes, and a click cannot quietly navigate away from it.
 */

import { Provider } from 'react-redux';
import type { ComponentType, ReactElement } from 'react';
import type { MultiWorkflowState } from '../types';

export interface StoryState {
  intl?: { locale: string; messages?: Record<string, string> };
  multiworkflow?: MultiWorkflowState;
  [key: string]: unknown;
}

const baseState: StoryState = {
  intl: { locale: 'en', messages: {} },
};

function makeStore(state: StoryState) {
  return {
    getState: () => state,
    subscribe: () => () => {},
    dispatch: (action: unknown) => action,
    replaceReducer: () => {},
  };
}

/**
 * Build a decorator wrapping a story in a `Provider`.
 *
 * @param state Merged over a base that always carries `intl.locale`.
 */
export function withStore(state: StoryState = {}) {
  return function StoreDecorator(Story: ComponentType): ReactElement {
    const store = makeStore({ ...baseState, ...state });
    return (
      // The fake store satisfies the parts of the API the components use.
      <Provider store={store as never}>
        <Story />
      </Provider>
    );
  };
}
