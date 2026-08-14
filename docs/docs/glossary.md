---
myst:
  html_meta:
    "description": "Terms and definitions used throughout the collective.multiworkflow documentation."
    "property=og:description": "Terms and definitions used throughout the collective.multiworkflow documentation."
    "property=og:title": "Glossary"
    "keywords": "Plone, collective.multiworkflow, glossary, term, definition"
---

(glossary-label)=

# Glossary

```{glossary}
:sorted: true

additional workflow
    A workflow contributed to a content object's {term}`chain` by a {term}`participating behavior`.
    An additional workflow never drives `review_state` and is never the first workflow of a chain.

chain
    The ordered tuple of workflows that apply to one content object.
    The workflow configured for the object's content type comes first; contributed workflows follow.

contribution
    The set of workflow ids one behavior marker adds to the chain of content providing it.
    Declared with the `<plone:additionalworkflows />` directive.

participating behavior
    A behavior whose marker interface extends `IAdditionalWorkflows`.
    Content providing such a marker resolves its chain through this package's adapter.

primary workflow
    The first workflow of a {term}`chain`: the one the content type is configured with, and the one driving `review_state`.

qualified state value
    A value as the `workflow_states` index holds it, reading `<workflow-id>|<state-id>`.
    Build one with `format_state` and read one back with `parse_state`.

state variable
    The variable a workflow records its state in, named by its `state_variable` setting.
    `review_state` for Plone's publication workflow; `workflow_states` for an {term}`additional workflow`.

Diátaxis
    A [framework](https://diataxis.fr/) for structuring technical documentation around four needs: tutorials, how-to guides, reference, and explanation.

MyST
    [Markedly Structured Text](https://myst-parser.readthedocs.io/en/latest/), the Markdown flavor this documentation is written in.

Plone
    [Plone](https://plone.org/) is an open source content management system used to create, edit, and manage digital content, including websites, intranets, and custom solutions.

plone.restapi
    The [REST API](https://6.docs.plone.org/plone.restapi/docs/source/index.html) Plone serves, and the package providing it.

Volto
    [Volto](https://6.docs.plone.org/volto/index.html) is Plone's React-based frontend.

behavior
    A reusable, optional capability that can be enabled per content type in Plone.
    This package uses behaviors as the unit of workflow assignment.

add-on
    A package that extends Plone's functionality.
```
