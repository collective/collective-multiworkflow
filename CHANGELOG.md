# Change log

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->
## 1.0.0a2 (2026-09-13)

### Backend


#### Feature

- Added `workflow_states` to the REST API serialization of every Dexterity object, and to the summaries of catalog results, so an object's state in every workflow of its chain comes back with the object or the listing itself. The key is added by wrapping `plone.restapi`'s `SerializeToJson.__call__` in place, so its folder and collection serializers, and any serializer an add-on derives from them, carry it too. @ericof [#8](https://github.com/collective/collective-multiworkflow/issues/8)
- Added an optional `label` attribute to the `<plone:additionalworkflows />` directive, naming the workflow in the user interface in place of its title. The label is translatable, in the `i18n_domain` of the ZCML file declaring it: the `@workflow` endpoint reports it as the chain entry's `title`, and the vocabulary of the Review state collection criterion names the workflow's states with it. A directive with a `label` must list exactly one workflow; without one, the workflow's title is used as before. @ericof [#9](https://github.com/collective/collective-multiworkflow/issues/9)


#### Bugfix

- Fixed imported content keeping the role mappings of its workflows' initial states. `plone.exportimport` restores workflow state by writing `workflow_history` directly, which fires no transition, so an additional workflow's permission map was never applied: an object imported as `active` kept the security of `pending`, unless some later event happened to recompute it. The existing patch to `update_workflow_history` now also reapplies each workflow's permission map for the restored state, and reindexes the object's security when a mapping changed. Content imported before this fix is repaired by running `updateRoleMappings` on `portal_workflow`. @ericof [#6](https://github.com/collective/collective-multiworkflow/issues/6)
- Loaded the `Products.CMFEditions` permission definitions before registering the `@history` service. Startup no longer fails with a `ComponentLookupError` for `CMFEditions.AccessPreviousVersions` when another package includes this one before `Products.CMFEditions` has been configured. @ericof [#7](https://github.com/collective/collective-multiworkflow/issues/7)
- Left a `review_state` collection criterion whose values name no workflow on the stock `review_state` index, instead of moving it onto `workflow_states` and qualifying its values with the site's default workflow. A collection written before the add-on was installed now answers exactly as it did, including for content types driven by another workflow, until it is saved again from the collection editor. @ericof [#10](https://github.com/collective/collective-multiworkflow/issues/10)


#### Internal

- Added tests pinning down the behavior the documentation describes: what enabling a participating behavior does to existing content, the order in which several behaviors' workflows are appended, how `plone.api` itself behaves on a chain with an additional workflow, what Classic UI's State menu and history viewlet show, the guard and subscriber patterns for making one workflow respond to another, each check the troubleshooting guide gives, and the tutorial followed step by step from its own workflow definition and ZCML. @ericof 
- Regenerated the message catalogs, picking up the reworded description of the example content profile. @ericof 
- Reorganized the backend into `utils`, `indexers`, `subscribers` and `restapi` subpackages. The `workflow_states` value helpers — `format_state`, `parse_state`, `WORKFLOW_STATES` and `STATE_SEPARATOR` — now live in `collective.multiworkflow.utils.workflow`, `reindex_workflow_states` in `collective.multiworkflow.subscribers.reindex`, and the REST API classes in `collective.multiworkflow.restapi.serializer.workflow` and `collective.multiworkflow.restapi.services`. Every one of them remains importable from its 1.0.0a1 location, except the `workflow_states` indexer function, whose name `collective.multiworkflow.indexers.workflow_states` now belongs to the module holding it. @ericof 


#### Documentation

- Corrected the docstring of `owning_workflow`, which claimed it resolves a shared transition id the way `doActionFor` does; it attributes the id to the first workflow defining it, while `doActionFor` picks the first workflow able to execute it. @ericof 



### Frontend


#### Feature

- Added support for the `workflow_states` key the backend serializes on content and on catalog summaries. `StateBadge` now also renders from a `workflow_states` value with an optional translated `label`, so a listing shows every item's states without requesting `@workflow` for each. New exports: the `getWorkflowStates`, `getAdditionalWorkflowStates`, `parseWorkflowState` and `formatWorkflowState` helpers, the `WORKFLOW_STATE_SEPARATOR` and `WORKFLOW_STATES_VOCABULARY` constants, and the `WorkflowStateValue`, `ParsedWorkflowState` and `WithWorkflowStates` types. @ericof [#8](https://github.com/collective/collective-multiworkflow/issues/8)


#### Bugfix

- Extracted the add-on's own user-facing strings into the i18n catalogs. `volto.pot` and the per-language catalogs held only their header, so every string the `Workflow` and `History` components define rendered untranslated whatever the site's language. @ericof [#2](https://github.com/collective/collective-multiworkflow/issues/2)


#### Internal

- Documented that a chain entry's `title` carries the `label` declared for the workflow on the backend, or the workflow's own title when none is declared, and added a labelled workflow to the story fixtures, stories and tests. @ericof [#9](https://github.com/collective/collective-multiworkflow/issues/9)



### Project


#### Internal

- Built the documentation on every change to the backend or the frontend, not only on changes under `docs/`. The Pages deploy is triggered by frontend changes and downloads the artifact this build produces from the same run, so a skipped build left it with nothing to download. @ericof 
- Exempted Dependabot pull requests from the changelog check, by labelling them `dependencies` and `skip changelog`. @ericof 
- Fixed the documentation and Storybook builds failing on branches whose name contains a slash, which the artifact upload rejects. @ericof 


#### Documentation

- Documented that importing content restores role mappings as well as catalog entries, and how to repair the security of content imported before that fix. @ericof [#6](https://github.com/collective/collective-multiworkflow/issues/6)
- Documented the `workflow_states` key in the content serialization and in summaries of catalog results, with generated request and response examples, described how to read every workflow's state through the REST API, and showed how to render those states in a Volto listing. @ericof [#8](https://github.com/collective/collective-multiworkflow/issues/8)
- Documented the `label` attribute of the `<plone:additionalworkflows />` directive, and where a declared label replaces the workflow's title. @ericof [#9](https://github.com/collective/collective-multiworkflow/issues/9)
- Documented when a `review_state` criterion is moved onto the `workflow_states` index and when it is left on the stock `review_state` index. @ericof [#10](https://github.com/collective/collective-multiworkflow/issues/10)
- Added a compatibility reference listing the release status, the Plone, Python, and Volto versions the test suites run against, what Classic UI shows, the changelogs, and where each package is published, and a status line on the home page linking to it. @ericof 
- Added a concepts page on when an additional workflow fits, with membership, translation status, and records retention scenarios and the signs of a problem that calls for something else, and linked it from the home page. @ericof 
- Added a guide to making one workflow react to another: a guard expression that reads another workflow's state through `portal_workflow.getInfoFor`, and an `IAfterTransitionEvent` subscriber that transitions another workflow. @ericof 
- Added a troubleshooting guide covering a chain missing its additional workflow, a transition reaching the wrong workflow, access changing after another workflow's transition, a search by an additional state that finds nothing, Volto showing only the publication workflow, content that predates a behavior, and an unexpected chain order. @ericof 
- Added an upgrade guide, covering the move from 1.0.0a1 to 1.0.0a2: the moved backend modules, the `review_state` criteria left on the stock index, repairing the role mappings of content imported with 1.0.0a1, the new `workflow_states` key in REST API responses, workflow labels, and what changes for Volto projects. @ericof 
- Added the package badges to the documentation landing page, matching the readme, and taught the Vale vocabulary and the linkcheck ignore list about them. @ericof 
- Corrected how the documentation describes a transition id shared by two workflows in a chain: `doActionFor` executes it in the first workflow that can execute it from its current state, not in the first workflow that defines it, so the workflow a transition is listed under can differ from the one it moves. @ericof 
- Documented the order in which several behaviors' workflows are appended to a chain, the reverse of the order the behaviors are listed on the type, correcting the concept page that said registration order. Documented as well that enabling a participating behavior on a type with content leaves existing objects unindexed under their new workflow and without its permission map, and the two calls that repair both. @ericof 
- Documented what the workflow helpers of `plone.api.content` do on content with an additional workflow, and made the transition ids in the guide to writing a composing workflow follow the guide's own prefixing advice. @ericof 
- Documented which shadow applies when another Volto add-on in the project also shadows the `Workflow` or `History` component. @ericof 
- Fixed the installation guide's verification step, which described an empty query result for code that checks the index exists, and showed the optional `label` attribute in the tutorial's directive example. @ericof 
- Fixed the workflow definition in the tutorial and the fragments of it in the guide to writing a composing workflow: DCWorkflow refused to import it because its transitions lacked the required `before_script` and `after_script` attributes, and without an `<action>` element its transitions would never have been offered to users. @ericof 
- Pointed the Python API reference, the how-to guides and the tutorial at the backend's new module layout, and added reference pages for `collective.multiworkflow.utils.workflow` and `collective.multiworkflow.subscribers.reindex`. @ericof 
- Removed closing sentences that added no information, and linked the facts the tutorial relied on before introducing them: the shared state variable, transition id collisions, what enabling a behavior does to existing content, the API helpers, and the format of the catalog index. @ericof 
- Split the REST API reference's compatibility table into unchanged, added and changed payloads, stated the narrowed `transitions` list as the one change to an existing key, moved the disclosure that `plone.restapi`'s content serializer is patched to the top of its section, and noted that the demo's bare transition ids predate the prefixing advice. @ericof 



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



