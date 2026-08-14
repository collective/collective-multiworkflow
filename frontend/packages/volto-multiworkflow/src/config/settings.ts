import type { ConfigType } from '@plone/registry';

export default function install(config: ConfigType) {
  // Nothing to register: the additional workflows are rendered by the shadowed
  // `Workflow` component (see src/customizations/), which puts them in the same
  // control as the publication workflow rather than in a separate menu entry.
  return config;
}
