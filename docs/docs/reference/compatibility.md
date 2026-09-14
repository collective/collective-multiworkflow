---
myst:
  html_meta:
    "description": "The release status of collective.multiworkflow, the Plone, Python, and Volto versions its test suites run against, and its support for Classic UI."
    "property=og:description": "The release status of collective.multiworkflow, the Plone, Python, and Volto versions its test suites run against, and its support for Classic UI."
    "property=og:title": "Compatibility"
    "keywords": "Plone, collective.multiworkflow, compatibility, Python, Volto, Classic UI, changelog"
---

(reference-compatibility)=

# Compatibility

This page lists the versions this repository's continuous integration tests against, and the state of each user interface.

## Release status

Both packages are in alpha.

| Package | Status |
|---|---|
| `collective.multiworkflow` | Alpha, with the `Development Status :: 3 - Alpha` classifier. |
| `@plone-collective/volto-multiworkflow` | Alpha, with a `-alpha` version suffix. |

The Python API, the REST API additions, and the Volto components may change before 1.0.0.
Read the changelog before upgrading, and follow {doc}`/how-to-guides/upgrade` from one release to the next.

The latest release of each package is listed on [PyPI](https://pypi.org/project/collective.multiworkflow/) and [npm](https://www.npmjs.com/package/@plone-collective/volto-multiworkflow).

## Backend

The backend test suite runs for every combination below, against the latest release of each Plone series.

| Plone | Python 3.11 | Python 3.12 | Python 3.13 | Python 3.14 |
|---|---|---|---|---|
| 6.2 | Tested | Tested | Tested | Tested |
| 6.1 | Tested | Tested | Tested | Tested |

The matrix is defined in [`.github/workflows/backend.yml`](https://github.com/collective/collective-multiworkflow/blob/main/.github/workflows/backend.yml).

```{note}
The package's metadata declares `Framework :: Plone :: 6.2` alone, and {doc}`/how-to-guides/install` assumes Plone 6.2.
Plone 6.1 is tested, but not declared.
```

## Frontend

Code analysis, internationalization checks, and unit tests for the frontend run against the following versions.

| Dependency | Version |
|---|---|
| Volto | 19.3.0 |
| Node.js | 24 |
| React | 18, as a peer dependency |

The add-on shadows Volto's `Workflow` and `History` components.
A Volto release that changes either component needs the shadows brought up to date, as {doc}`/how-to-guides/customize-the-volto-components` describes.

## User interfaces

| Interface | Status |
|---|---|
| Volto | Supported. The add-on renders a selector for each workflow in the chain and the merged history. |
| Classic UI | Not supported. The package ships no Classic UI integration. |

(reference-compatibility-classic-ui)=

### Without Volto

Classic UI keeps working on content with additional workflows, but it has no notion of a chain of more than one workflow.

- The **State** menu lists the transitions of every workflow in the chain in one flat list.
- The history viewlet shows the history of the publication workflow alone.

The test suite asserts both, in `backend/tests/classicui/test_classic_ui.py`.

## Changelogs

- [Repository changelog](https://github.com/collective/collective-multiworkflow/blob/main/CHANGELOG.md), covering both packages.
- [`collective.multiworkflow` changelog](https://github.com/collective/collective-multiworkflow/blob/main/backend/CHANGELOG.md).
- [`@plone-collective/volto-multiworkflow` changelog](https://github.com/collective/collective-multiworkflow/blob/main/frontend/packages/volto-multiworkflow/CHANGELOG.md).
