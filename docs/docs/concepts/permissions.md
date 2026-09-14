---
myst:
  html_meta:
    "description": "Why concurrent workflows must manage disjoint permission sets, and why this package reports an overlap rather than arbitrating it."
    "property=og:description": "Why concurrent workflows must manage disjoint permission sets, and why this package reports an overlap rather than arbitrating it."
    "property=og:title": "About permissions in a chain"
    "keywords": "Plone, collective.multiworkflow, permissions, role mappings, workflow, security"
---

(concepts-permissions)=

# About permissions in a chain

Controlling access that the publication workflow does not control is one of the best reasons to add a second workflow.
Doing so safely depends on one constraint, and this page explains where that constraint comes from.

## What a transition actually rewrites

A DCWorkflow state carries a permission map: for each permission the workflow declares, the roles that hold it in that state.
When an object transitions, `updateRoleMappingsFor` writes that map onto the object.

The important detail is what it does *not* write.
It rewrites only the permissions listed in that workflow's own `permissions` list, and it leaves every other permission on the object alone.
A transition also re-applies the mappings of the transitioning workflow alone; the other workflows in the chain are not consulted and their maps are not reapplied.

That behavior is what makes concurrent workflows possible at all.
Two workflows managing two different permission sets simply write to two different parts of the object's security, in any order, with no interference.

## The constraint

**No two workflows in a chain may manage the same permission.**

Where two do, the object's mapping for that permission is whichever of them transitioned last.
It stays that way until the other workflow transitions, or until `portal_workflow.updateRoleMappings()` runs over the site.

```{warning}
This failure mode is quiet.
Nothing raises, nothing is logged, and the object keeps working.
It simply grants—or withholds—access according to a workflow that is no longer the one the site's designer had in mind, and the effective mapping flips every time either workflow transitions.
```

The rest of the composition rules follow the same logic.
Transition ids must be unique across the chain, because `doActionFor` executes an ambiguous id in the first workflow, in chain order, that can execute it from its current state.
Which workflow moves then depends on the states the object happens to be in, and only naming the workflow explicitly takes that choice away from them.

## Why the package reports rather than arbitrates

An overlap is detectable.
`conflicting_permissions` walks the chain, collects the permissions each workflow declares, and returns those with more than one claimant.

It would be technically possible to go further—to merge the maps, to rank workflows, to make the last transition win deliberately rather than accidentally.
This package does none of that, for two reasons.

**There is no correct answer.**
Merging two permission maps means choosing between intersection and union: the first can lock out a user the site intended to admit, the second can admit one it intended to lock out. Neither is a safe default for a security setting, and the choice depends on what the two workflows mean, which is knowledge the package does not have.

**A silent resolution is worse than a loud constraint.**
Arbitration would make the overlap survivable and therefore invisible, and sites would accumulate chains whose effective security nobody could derive by reading either workflow.
Reporting keeps the constraint where a person can see it: in the workflow definitions, at the time they are written.

So the package's position is that an overlap is a design error in the workflows, and its job is to make that error easy to find.

```{seealso}
{doc}`/how-to-guides/audit-permission-conflicts` for how to run the check, and {doc}`/how-to-guides/write-a-composing-workflow` for how to avoid needing it.
```
