---
myst:
  html_meta:
    "description": "The additions this package makes to the @workflow and @history endpoints of plone.restapi, and to the serialization of content."
    "property=og:description": "The additions this package makes to the @workflow and @history endpoints of plone.restapi, and to the serialization of content."
    "property=og:title": "REST API"
    "keywords": "Plone, collective.multiworkflow, REST, API, workflow, history, serialization, workflow_states"
---

(reference-rest-api)=

# REST API

This package extends {term}`plone.restapi` in three places: the `@workflow` and `@history` endpoints, and the serialization of content itself.
Almost every change is an addition, and every key the API already returned keeps its value, with one exception: the top-level `transitions` list of `@workflow` on participating content, described under {ref}`reference-rest-api-compatibility`.

The additions to `@workflow` and `@history` apply to participating content only.
Content that provides no participating behavior is served exactly the payload core produces there, as shown under [Content without additional workflows](#content-without-additional-workflows).

The `workflow_states` key of the content serialization is the exception.
It is added to every Dexterity object, participating or not, because every object with a workflow has a value for it.

```{seealso}
The endpoints these extend are documented in the Plone REST API reference, under [Workflow](https://6.docs.plone.org/plone.restapi/docs/source/endpoints/workflow.html) and [History](https://6.docs.plone.org/plone.restapi/docs/source/endpoints/history.html).
Content serialization and summaries are described under [Serialization](https://6.docs.plone.org/plone.restapi/docs/source/usage/serialization.html) and [Search](https://6.docs.plone.org/plone.restapi/docs/source/endpoints/searching.html).
```

(reference-rest-api-workflow-get)=

## `GET @workflow`

Returns the workflow information for a content object.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../backend/tests/docs/http-examples/workflow_get.req
```

```{literalinclude} ../../../backend/tests/docs/http-examples/workflow_get.resp
:language: http
```

### The `chain` key

`chain` holds one entry per workflow applying to the object, in chain order.
The first entry is always the workflow configured for the content type—the one driving `review_state`.
Contributed workflows follow, in the order {ref}`reference-zcml-order` describes.

Each entry holds the following keys.

`workflow_id`
:   Id of the workflow, as `portal_workflow` registers it.

`title`
:   The name to show for the workflow, translated: the `label` declared on its `<plone:additionalworkflows />` directive, or the workflow's own title when none is declared.
    See {ref}`reference-zcml`.

`state_variable`
:   The variable this workflow drives.
    `review_state` for the primary workflow; never `review_state` for an additional one.

`state`
:   The object's current state in this workflow, as an object with `id` and a translated `title`.
    The title comes from the workflow's own state definition, so it resolves for a contributed workflow that the content type's configured chain does not mention.

`transitions`
:   The transitions of this workflow available to the current user, each with an `@id` to `POST` to and a translated `title`.
    A transition id defined by more than one workflow in the chain is attributed to the first workflow that defines it, which is how `doActionFor` resolves the same collision.

`history`
:   This workflow's own `review_history` entries.
    A workflow that records no history reports an empty list.

### The top-level `transitions` key

For participating content, the top-level `transitions` list is narrowed to the primary workflow's transitions.

This is deliberate.
A client written before this package existed reads that list and offers its contents as publication actions; widening it would make an unrelated workflow's transitions appear in a publication menu.
Every transition remains available under `chain`, grouped by the workflow that owns it.

(content-without-additional-workflows)=

### Content without additional workflows

A content object providing no participating behavior is served core's payload, with no `chain` key.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../backend/tests/docs/http-examples/workflow_get_plain.req
```

```{literalinclude} ../../../backend/tests/docs/http-examples/workflow_get_plain.resp
:language: http
```

```{important}
Test for the presence of the `chain` key rather than assuming it.
A client that reads `chain` unconditionally breaks on the first non-participating object it meets.
```

(reference-rest-api-workflow-post)=

## `POST @workflow/{transition}`

Executes a transition.
This endpoint is core's, unchanged: a transition belonging to an additional workflow is executed exactly like a publication transition, using the `@id` reported for it under `chain`.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../backend/tests/docs/http-examples/workflow_post.req
```

```{literalinclude} ../../../backend/tests/docs/http-examples/workflow_post.resp
:language: http
```

```{note}
The examples on this page use the example membership workflow the demo package ships, whose transition ids are `activate` and `lapse`.
Those bare ids predate the advice to prefix transition ids with something specific to their workflow, such as `membership_activate`, which {doc}`/how-to-guides/write-a-composing-workflow` gives.
Prefer prefixed ids in a workflow of your own.
```

The response reports `review_state`, as it always has.
A transition belonging to an additional workflow does not change it—read the new state from `chain` with a follow-up `GET`, or from the `@workflow` expansion of the object.

(reference-rest-api-history)=

## `GET @history`

Returns the history of every workflow in the chain, merged into one stream, newest first.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../backend/tests/docs/http-examples/history_get.req
```

```{literalinclude} ../../../backend/tests/docs/http-examples/history_get.resp
:language: http
```

### The `workflow_id` key

Every entry carries a `workflow_id`, including the ones core produces.

- For a workflow entry, it is the id of the workflow that recorded the transition.
- For a versioning entry, it is `null`.
  Such an entry belongs to no workflow.

The key is present on every entry, so a client may read it without a guard.

Entries are otherwise shaped exactly as core shapes them, and carry the same keys.
A workflow entry also carries its own workflow's state variable: `review_state` for the primary workflow, and whatever variable an additional workflow declares.

```{note}
Each workflow's `review_history` is read separately, so each workflow's own info guard decides whether its entries are visible to the current user.
An entry the guard hides is absent rather than redacted.
```

(reference-rest-api-content)=

## Content serialization

The serialization of a content object—what `GET` on its URL returns—gains a `workflow_states` key.

```{important}
The key is added by patching `plone.restapi`.
When this package's ZCML is loaded, the `__call__` method of `plone.restapi`'s `SerializeToJson` class is wrapped in place.
Its folder and collection serializers, and any serializer an add-on derives from them, reach that method through `super()`, so they carry the key too.
A serializer overriding `__call__` without calling `super()` does not, and neither does the Plone site root, which has a serializer of its own.
```

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../backend/tests/docs/http-examples/content_get.req
```

```{literalinclude} ../../../backend/tests/docs/http-examples/content_get.resp
:language: http
```

### The `workflow_states` key

`workflow_states` holds the object's state in every workflow of its chain, one `<workflow-id>|<state-id>` value per workflow, in chain order.
These are exactly the values the `workflow_states` catalog index holds, as described in {doc}`catalog`.

- The first value is always the workflow driving `review_state`, and it agrees with the `review_state` key of the same payload.
- The key is present on every Dexterity object.
  An object with no workflow at all reports an empty list.
- For a historical version, requested through `GET @history/{version}`, the states are read from that version, which is where `review_state` is read from too.

(reference-rest-api-summary)=

### Summaries of catalog results

Summaries built from catalog results carry `workflow_states` as well, read from the metadata column of the same name.
That covers the items of a folder and the results of `@search` and `@querystring-search`.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../backend/tests/docs/http-examples/search_get.req
```

```{literalinclude} ../../../backend/tests/docs/http-examples/search_get.resp
:language: http
```

A client can therefore show each item's state in every workflow without one request per item.

(reference-rest-api-compatibility)=

## Compatibility

The tables below compare each payload with what `plone.restapi` returns without this package.

### Unchanged

| Payload | Behavior |
|---|---|
| `@workflow` on non-participating content | core's payload |
| `@workflow` keys other than `transitions` | core's values |
| `POST @workflow/{transition}` | core's behavior |

### Added

| Payload | Addition |
|---|---|
| `@workflow` on participating content | a `chain` key |
| `@history` entries on participating content | a `workflow_id` key |
| Content serialization | a `workflow_states` key |
| Summaries of catalog results | a `workflow_states` field |

### Changed

| Payload | Without this package | With this package |
|---|---|---|
| `@workflow` `transitions` on participating content | every transition the chain offers | the primary workflow's transitions only |

A client that relies on the top-level `transitions` list to reach every workflow's transitions must read them from `chain` instead.
Only a site whose chains already held several workflows before this package was installed can have such a client, because on a chain of one workflow the two lists hold the same transitions.

The examples on this page are generated by the test suite, in `backend/tests/docs/`, and are regenerated on every run.
A payload that changes shape without the documentation changing with it fails the suite.
