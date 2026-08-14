# Changelog

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->

## 1.0.0-alpha.1 (2026-08-14)


### Feature

- Added components for rendering additional workflows: a shadowed `Workflow` control that renders one selector per workflow in the chain, a shadowed `History` view that reads a merged history correctly, `AdditionalWorkflowMenu` showing each additional workflow's state and available transitions, and `StateBadge` rendering one state for listings. The `History` view derives each entry's previous state per `workflow_id` rather than from the entry preceding it in the list — the latter invents transitions between unrelated workflows once `@history` merges a chain into one stream — and names the workflow on every row when a history spans more than one. Everything is driven by the `chain` key of the `@workflow` response, so content without additional workflows renders exactly what Plone has always rendered. Typed interfaces for both payloads are exported. @ericof 


### Documentation

- Stated the supported Plone version as 6.2 in the readme, matching the backend package. @ericof
