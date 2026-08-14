# Change log

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->
## 1.0.0a1 (2026-08-14)

### Backend


#### Feature

- Added support for assigning additional workflows to content types through behaviors. A behavior marker extending `IAdditionalWorkflows` declares the workflows it contributes with a `<plone:additionalworkflows />` ZCML directive, and those are appended to the type's configured workflow chain — never replacing it. An additional workflow leaves `review_state` untouched, and may manage permissions of its own as long as the sets are disjoint across the chain — `conflicting_permissions` audits an object for overlap. The whole chain is searchable through one `workflow_states` KeywordIndex and metadata column, whose values read `<workflow-id>|<state-id>` in chain order with the type's configured workflow always first, so a site gains no further indexes as more workflows are contributed; a workflow adopting `workflow_states` as its `state_variable` is reindexed by CMFCore itself, and one keeping a state variable of its own is kept fresh by a transition subscriber. Additional workflows are exposed through workflow-aware API helpers, a `chain` key on the `@workflow` REST API endpoint, and an `@history` listing that merges every workflow's transitions into one stream, each entry tagged with its `workflow_id`. Content without a participating behavior is unaffected, and the package ships no behavior of its own — the worked example lives in the `collective.multiworkflow.demo` subpackage, which is not loaded by default. @ericof 


#### Documentation

- Stated the supported Plone version as 6.2 in the readme, matching the package classifiers. @ericof 



### Frontend


#### Feature

- Added components for rendering additional workflows: a shadowed `Workflow` control that renders one selector per workflow in the chain, a shadowed `History` view that reads a merged history correctly, `AdditionalWorkflowMenu` showing each additional workflow's state and available transitions, and `StateBadge` rendering one state for listings. The `History` view derives each entry's previous state per `workflow_id` rather than from the entry preceding it in the list — the latter invents transitions between unrelated workflows once `@history` merges a chain into one stream — and names the workflow on every row when a history spans more than one. Everything is driven by the `chain` key of the `@workflow` response, so content without additional workflows renders exactly what Plone has always rendered. Typed interfaces for both payloads are exported. @ericof 


#### Documentation

- Stated the supported Plone version as 6.2 in the readme, matching the backend package. @ericof 



### Project


#### Feature

- Added multi-workflow support for Plone: content types can gain additional workflows through behaviors, each tracking its own state alongside the publication workflow, with per-workflow state and transitions exposed in the `@workflow` REST API endpoint, every workflow's transitions reported by `@history`, and the whole workflow chain searchable through a single `workflow_states` catalog index. @ericof 


#### Internal

- Fixed the CI workflow not starting on a push. Its `paths` filter was `*`, which matches only files at the repository root, so any change confined to `backend/`, `frontend/`, `docs/` or `news/` triggered no run. Per-area gating already happens in the `config` job. @ericof 


#### Documentation

- Added the tutorial "Manage additional workflows in Volto", walking through the toolbar control, a transition that leaves `review_state` untouched, and the merged history, with screenshots. @ericof 
- Added two how-to guides: "How to consume the REST API", covering the `chain` key, transitions and the merged history from a client of your own, and "How to customize the Volto components", covering restyling, reuse, and shadowing. @ericof 
- Corrected the installation guide: the Volto add-on is added as a frontend dependency and registered in `volto.config.js`, and the backend profile is installed through a GenericSetup dependency or the add-ons control panel rather than a call to `runAllImportStepsFromProfile`. @ericof 
- Disclosed on the documentation landing page that these pages were written with Claude Opus 5, following the Plone documentation style skill, and reviewed by a human being. @ericof 
- Presented the tutorials, how-to guides, concepts, and reference indexes as card grids, matching the documentation root. @ericof 
- Stated the supported Plone version as 6.2 throughout the documentation and the readme files, matching the package classifiers. @ericof 



