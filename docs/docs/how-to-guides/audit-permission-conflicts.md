---
myst:
  html_meta:
    "description": "Find permissions claimed by more than one workflow in a chain, and resolve the overlap."
    "property=og:description": "Find permissions claimed by more than one workflow in a chain, and resolve the overlap."
    "property=og:title": "How to audit permission conflicts"
    "keywords": "Plone, collective.multiworkflow, permissions, role mappings, audit"
---

(howto-audit-permission-conflicts)=

# How to audit permission conflicts

This guide shows you how to find permissions claimed by more than one workflow in a chain, and what to do about one.

Run this whenever you add a workflow to a chain you did not write in full—an upgrade step is a good place for it, and so is a test.

## Prerequisites

- Content participating in at least one additional workflow.

## 1. Audit one object

```python
from collective.multiworkflow import api as mw_api

conflicts = mw_api.conflicting_permissions(obj)
```

An empty mapping means the chain is conflict-free.
Anything else maps a permission to the ids of the workflows claiming it, in chain order.

```python
{
    "Modify portal content": [
        "simple_publication_workflow",
        "foundation_member_workflow",
    ]
}
```

## 2. Audit a whole site

Walk one object per participating type—the chain is a property of the type, not of the object, so one sample per type is enough.

```python
from plone import api

seen = set()
for brain in api.content.find(portal_type=["Profile", "Document"]):
    obj = brain.getObject()
    if obj.portal_type in seen:
        continue
    seen.add(obj.portal_type)
    conflicts = mw_api.conflicting_permissions(obj)
    if conflicts:
        print(obj.portal_type, conflicts)
```

## 3. Resolve an overlap

There is only one durable fix: stop two workflows from managing the same permission.

- **Preferred.** Remove the permission from one workflow's `permissions` list, and reapply that workflow's profile.
  Decide which workflow is the one that should own it, and let the other stop claiming it.
- **Alternative.** Define a permission of your own for the additional workflow, and guard your own views and transitions with that instead of reusing a permission the publication workflow already manages.

After changing a workflow definition, re-run the role mappings so existing content picks the change up.

```python
wftool = api.portal.get_tool("portal_workflow")
wftool.updateRoleMappings()
```

```{warning}
`updateRoleMappings()` rewrites the mappings of every object in the site and is expensive.
It also only re-establishes a consistent state at the moment it runs: with an unresolved overlap still in place, the next transition of either workflow puts the object back into last-writer-wins.
It is a repair, not a fix.
```

## 4. Keep it audited

Assert on it in your add-on's test suite, so a workflow added later cannot reintroduce the overlap unnoticed.

```python
def test_chain_has_no_permission_conflicts(member_profile):
    assert mw_api.conflicting_permissions(member_profile) == {}
```

```{seealso}
{doc}`/concepts/permissions` for why an overlap behaves the way it does, and why this package reports it rather than resolving it.
```
