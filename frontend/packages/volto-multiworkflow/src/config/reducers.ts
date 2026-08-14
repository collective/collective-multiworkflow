import type { ConfigType } from '@plone/registry';
import multiworkflow from '../reducers/multiworkflow';

export default function install(config: ConfigType) {
  // The chain is not in Volto's own workflow reducer, which keeps only state,
  // history and transitions from the response.
  config.addonReducers = {
    ...config.addonReducers,
    multiworkflow,
  };
  return config;
}
