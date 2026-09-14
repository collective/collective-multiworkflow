# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 1.0.0a2 (2026-09-13)


### Feature

- Added `workflow_states` to the REST API serialization of every Dexterity object, and to the summaries of catalog results, so an object's state in every workflow of its chain comes back with the object or the listing itself. The key is added by wrapping `plone.restapi`'s `SerializeToJson.__call__` in place, so its folder and collection serializers, and any serializer an add-on derives from them, carry it too. @ericof [#8](https://github.com/collective/collective-multiworkflow/issues/8)
- Added an optional `label` attribute to the `<plone:additionalworkflows />` directive, naming the workflow in the user interface in place of its title. The label is translatable, in the `i18n_domain` of the ZCML file declaring it: the `@workflow` endpoint reports it as the chain entry's `title`, and the vocabulary of the Review state collection criterion names the workflow's states with it. A directive with a `label` must list exactly one workflow; without one, the workflow's title is used as before. @ericof [#9](https://github.com/collective/collective-multiworkflow/issues/9)


### Bugfix

- Fixed imported content keeping the role mappings of its workflows' initial states. `plone.exportimport` restores workflow state by writing `workflow_history` directly, which fires no transition, so an additional workflow's permission map was never applied: an object imported as `active` kept the security of `pending`, unless some later event happened to recompute it. The existing patch to `update_workflow_history` now also reapplies each workflow's permission map for the restored state, and reindexes the object's security when a mapping changed. Content imported before this fix is repaired by running `updateRoleMappings` on `portal_workflow`. @ericof [#6](https://github.com/collective/collective-multiworkflow/issues/6)
- Loaded the `Products.CMFEditions` permission definitions before registering the `@history` service. Startup no longer fails with a `ComponentLookupError` for `CMFEditions.AccessPreviousVersions` when another package includes this one before `Products.CMFEditions` has been configured. @ericof [#7](https://github.com/collective/collective-multiworkflow/issues/7)
- Left a `review_state` collection criterion whose values name no workflow on the stock `review_state` index, instead of moving it onto `workflow_states` and qualifying its values with the site's default workflow. A collection written before the add-on was installed now answers exactly as it did, including for content types driven by another workflow, until it is saved again from the collection editor. @ericof [#10](https://github.com/collective/collective-multiworkflow/issues/10)


### Internal

- Added tests pinning down the behavior the documentation describes: what enabling a participating behavior does to existing content, the order in which several behaviors' workflows are appended, how `plone.api` itself behaves on a chain with an additional workflow, what Classic UI's State menu and history viewlet show, the guard and subscriber patterns for making one workflow respond to another, each check the troubleshooting guide gives, and the tutorial followed step by step from its own workflow definition and ZCML. @ericof 
- Regenerated the message catalogs, picking up the reworded description of the example content profile. @ericof 
- Reorganized the backend into `utils`, `indexers`, `subscribers` and `restapi` subpackages. The `workflow_states` value helpers — `format_state`, `parse_state`, `WORKFLOW_STATES` and `STATE_SEPARATOR` — now live in `collective.multiworkflow.utils.workflow`, `reindex_workflow_states` in `collective.multiworkflow.subscribers.reindex`, and the REST API classes in `collective.multiworkflow.restapi.serializer.workflow` and `collective.multiworkflow.restapi.services`. Every one of them remains importable from its 1.0.0a1 location, except the `workflow_states` indexer function, whose name `collective.multiworkflow.indexers.workflow_states` now belongs to the module holding it. @ericof 


### Documentation

- Corrected the docstring of `owning_workflow`, which claimed it resolves a shared transition id the way `doActionFor` does; it attributes the id to the first workflow defining it, while `doActionFor` picks the first workflow able to execute it. @ericof 

## 1.0.0a1 (2026-08-14)


### Feature

- Added support for assigning additional workflows to content types through behaviors. A behavior marker extending `IAdditionalWorkflows` declares the workflows it contributes with a `<plone:additionalworkflows />` ZCML directive, and those are appended to the type's configured workflow chain — never replacing it. An additional workflow leaves `review_state` untouched, and may manage permissions of its own as long as the sets are disjoint across the chain — `conflicting_permissions` audits an object for overlap. The whole chain is searchable through one `workflow_states` KeywordIndex and metadata column, whose values read `<workflow-id>|<state-id>` in chain order with the type's configured workflow always first, so a site gains no further indexes as more workflows are contributed; a workflow adopting `workflow_states` as its `state_variable` is reindexed by CMFCore itself, and one keeping a state variable of its own is kept fresh by a transition subscriber. Additional workflows are exposed through workflow-aware API helpers, a `chain` key on the `@workflow` REST API endpoint, and an `@history` listing that merges every workflow's transitions into one stream, each entry tagged with its `workflow_id`. Content without a participating behavior is unaffected, and the package ships no behavior of its own — the worked example lives in the `collective.multiworkflow.demo` subpackage, which is not loaded by default. @ericof 


### Documentation

- Stated the supported Plone version as 6.2 in the readme, matching the package classifiers. @ericof
