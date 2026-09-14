# Changelog

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->

## 1.0.0-alpha.2 (2026-09-13)


### Feature

- Added support for the `workflow_states` key the backend serializes on content and on catalog summaries. `StateBadge` now also renders from a `workflow_states` value with an optional translated `label`, so a listing shows every item's states without requesting `@workflow` for each. New exports: the `getWorkflowStates`, `getAdditionalWorkflowStates`, `parseWorkflowState` and `formatWorkflowState` helpers, the `WORKFLOW_STATE_SEPARATOR` and `WORKFLOW_STATES_VOCABULARY` constants, and the `WorkflowStateValue`, `ParsedWorkflowState` and `WithWorkflowStates` types. @ericof [#8](https://github.com/collective/collective-multiworkflow/issues/8)


### Bugfix

- Extracted the add-on's own user-facing strings into the i18n catalogs. `volto.pot` and the per-language catalogs held only their header, so every string the `Workflow` and `History` components define rendered untranslated whatever the site's language. @ericof [#2](https://github.com/collective/collective-multiworkflow/issues/2)


### Internal

- Documented that a chain entry's `title` carries the `label` declared for the workflow on the backend, or the workflow's own title when none is declared, and added a labelled workflow to the story fixtures, stories and tests. @ericof [#9](https://github.com/collective/collective-multiworkflow/issues/9)

## 1.0.0-alpha.1 (2026-08-14)


### Feature

- Added components for rendering additional workflows: a shadowed `Workflow` control that renders one selector per workflow in the chain, a shadowed `History` view that reads a merged history correctly, `AdditionalWorkflowMenu` showing each additional workflow's state and available transitions, and `StateBadge` rendering one state for listings. The `History` view derives each entry's previous state per `workflow_id` rather than from the entry preceding it in the list — the latter invents transitions between unrelated workflows once `@history` merges a chain into one stream — and names the workflow on every row when a history spans more than one. Everything is driven by the `chain` key of the `@workflow` response, so content without additional workflows renders exactly what Plone has always rendered. Typed interfaces for both payloads are exported. @ericof 


### Documentation

- Stated the supported Plone version as 6.2 in the readme, matching the backend package. @ericof
