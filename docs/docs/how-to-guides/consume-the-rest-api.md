---
myst:
  html_meta:
    "description": "Read an object's whole workflow chain from a REST client, execute an additional workflow's transition, and read the merged history."
    "property=og:description": "Read an object's whole workflow chain from a REST client, execute an additional workflow's transition, and read the merged history."
    "property=og:title": "How to consume the REST API"
    "keywords": "Plone, collective.multiworkflow, REST, API, client, workflow, history"
---

(howto-consume-the-rest-api)=

# How to consume the REST API

This guide shows you how to read and drive an object's additional workflows from a REST client.

Everything here uses endpoints {term}`plone.restapi` already exposes.
This package adds keys to their payloads rather than adding endpoints, so a client you have already written keeps working, and reaches the additional workflows by reading one more key.

## Prerequisites

- A site with `collective.multiworkflow` installed, as described in {doc}`install`.
- Content participating in at least one additional workflow.
- A client that authenticates against `plone.restapi` as it normally does.

## Read the whole chain

Request `@workflow` on the object.

```shell
curl -H "Accept: application/json" https://example.com/profiles/ortegas/@workflow
```

The response carries a `chain` key holding one entry per workflow, in chain order.

```json
{
  "@id": "https://example.com/profiles/ortegas/@workflow",
  "state": {"id": "published", "title": "Published"},
  "transitions": [
    {"@id": "https://example.com/profiles/ortegas/@workflow/retract", "title": "Retract"}
  ],
  "chain": [
    {
      "workflow_id": "simple_publication_workflow",
      "title": "Simple Publication Workflow",
      "state_variable": "review_state",
      "state": {"id": "published", "title": "Published"},
      "transitions": [
        {"@id": "https://example.com/profiles/ortegas/@workflow/retract", "title": "Retract"}
      ],
      "history": []
    },
    {
      "workflow_id": "foundation_member_workflow",
      "title": "Membership",
      "state_variable": "workflow_states",
      "state": {"id": "active", "title": "Active"},
      "transitions": [
        {"@id": "https://example.com/profiles/ortegas/@workflow/lapse", "title": "Lapse"}
      ],
      "history": []
    }
  ]
}
```

The first entry is always the workflow configured for the content type, the one driving `review_state`.
Every entry after it is an additional workflow.

## Guard on the `chain` key

Content that provides no participating behavior is served core's payload, with no `chain` key at all.
Test for the key rather than assuming it.

```js
const chain = workflow.chain ?? [];
const additional = chain.slice(1);
```

```{important}
A client that reads `chain` unconditionally breaks on the first non-participating object it meets.
Treat its absence as "this object has one workflow", not as an error.
```

## Read the chain without a second request

If you are already fetching the object, expand the workflow component instead of making a separate call.

```shell
curl -H "Accept: application/json" "https://example.com/profiles/ortegas?expand=workflow"
```

The expansion carries the same payload, including `chain`, under `@components.workflow`.

## Execute a transition

`POST` to the `@id` reported for the transition under `chain`.
The endpoint is core's, and a transition belonging to an additional workflow is executed exactly like a publication transition.

```shell
curl -X POST -H "Accept: application/json" \
  https://example.com/profiles/ortegas/@workflow/lapse
```

To record a comment, send it in the body.

```shell
curl -X POST -H "Accept: application/json" -H "Content-Type: application/json" \
  -d '{"comment": "Renewal window closed"}' \
  https://example.com/profiles/ortegas/@workflow/lapse
```

Take the `@id` from the payload rather than building the URL yourself.
A transition id defined by more than one workflow in the chain is attributed to the first workflow that defines it, and the reported `@id` already resolves that collision the way the workflow tool does.

## Re-read the state after a transition

The transition response reports `review_state`, as it always has.
A transition belonging to an additional workflow does not change `review_state`, so the response tells you nothing about the state you just moved.

Read the new state with a follow-up `GET`.

```shell
curl -H "Accept: application/json" https://example.com/profiles/ortegas/@workflow
```

```{important}
Do not reduce the transition response as if it were a workflow payload.
It is a single history entry, and a client that stores it in place of the workflow payload loses `chain` until the next full read.
```

## Read the merged history

Request `@history` on the object.

```shell
curl -H "Accept: application/json" https://example.com/profiles/ortegas/@history
```

Every workflow's transitions arrive in one stream, newest first, and every entry carries a `workflow_id`.

```json
[
  {
    "action": "lapse",
    "actor": "admin",
    "time": "2026-08-13T21:46:28+00:00",
    "workflow_id": "foundation_member_workflow",
    "type": "workflow"
  },
  {
    "action": "Edited",
    "actor": "admin",
    "time": "2026-08-13T21:46:03+00:00",
    "workflow_id": null,
    "type": "versioning"
  }
]
```

`workflow_id` is present on every entry, so you can read it without a guard.
It is `null` for a versioning entry, which belongs to no workflow.

To show only one workflow's entries, filter on it.

```js
const membership = history.filter(
  (entry) => entry.workflow_id === "foundation_member_workflow",
);
```

## Label an entry with its workflow

History entries carry a `workflow_id` but not the workflow's title.
Read the titles from the chain and map them.

```js
const titles = Object.fromEntries(
  (workflow.chain ?? []).map((entry) => [entry.workflow_id, entry.title]),
);

const label = (entry) => titles[entry.workflow_id] ?? null;
```

## Present the right transitions

For participating content, the top-level `transitions` list is narrowed to the primary workflow.

Use it wherever you present publication actions, and read `chain` for everything else.
This is what keeps an unrelated workflow's transitions out of a publication menu in a client written before this package existed.

```{seealso}
{doc}`/reference/rest-api` describes every key on both endpoints, with request and response examples generated by the test suite.

If you are writing a Volto interface rather than a client of your own, start from {doc}`customize-the-volto-components` instead.
```
