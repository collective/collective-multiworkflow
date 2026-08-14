---
myst:
  html_meta:
    "description": "The additions this package makes to the @workflow and @history endpoints of plone.restapi."
    "property=og:description": "The additions this package makes to the @workflow and @history endpoints of plone.restapi."
    "property=og:title": "REST API"
    "keywords": "Plone, collective.multiworkflow, REST, API, workflow, history"
---

(reference-rest-api)=

# REST API

This package extends two endpoints of {term}`plone.restapi`.
Both additions are additive: every key those endpoints already returned is returned unchanged, with the same value.

The additions apply to participating content only.
Content that provides no participating behavior is served exactly the payload core produces, as shown under [Content without additional workflows](#content-without-additional-workflows).

```{seealso}
The endpoints these extend are documented in the Plone REST API reference, under [Workflow](https://6.docs.plone.org/plone.restapi/docs/source/endpoints/workflow.html) and [History](https://6.docs.plone.org/plone.restapi/docs/source/endpoints/history.html).
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
Contributed workflows follow, in the order their behaviors contribute them.

Each entry holds the following keys.

`workflow_id`
:   Id of the workflow, as `portal_workflow` registers it.

`title`
:   The workflow's own title, translated.

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

## Compatibility

| Payload | Before | After |
|---|---|---|
| `@workflow` on non-participating content | core's payload | unchanged |
| `@workflow` keys other than `transitions` | core's values | unchanged |
| `@workflow` `transitions` on participating content | every transition the chain offered | narrowed to the primary workflow |
| `@history` entries | core's shape | one key added, `workflow_id` |
| `POST @workflow/{transition}` | core's behavior | unchanged |

The examples on this page are generated by the test suite, in `backend/tests/docs/`, and are regenerated on every run.
A payload that changes shape without the documentation changing with it fails the suite.
