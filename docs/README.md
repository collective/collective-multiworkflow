# Documentation

The Sphinx documentation for **Multi-Workflow Support for Plone**, built with [MyST](https://myst-parser.readthedocs.io/) and the [Plone Sphinx Theme](https://github.com/plone/plone-sphinx-theme).

Published at [collective.github.io/collective-multiworkflow](https://collective.github.io/collective-multiworkflow/).

## What is here

```
docs/
├── docs/          the documentation source; every page lives here
│   ├── conf.py    Sphinx configuration, commented section by section
│   ├── index.md   landing page
│   ├── tutorials/       learning-oriented
│   ├── how-to-guides/   task-oriented
│   ├── concepts/        understanding-oriented
│   └── reference/       information-oriented
├── styles/        Vale styles and the project vocabulary
├── Makefile       every command below
└── pyproject.toml documentation dependencies
```

The four content directories are the quadrants of the [Diátaxis](https://diataxis.fr/) framework.
Each page belongs to exactly one of them: a page that both teaches and describes belongs in two pages.

## Prerequisites

[uv](https://docs.astral.sh/uv/) manages the Python version and the dependencies.

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Everything else is installed on first use by the Makefile.

## Build and preview

| Command | What it does |
| --- | --- |
| `make html` | Build the HTML documentation into `_build/html`. |
| `make livehtml` | Rebuild on change and serve a live-reloading preview. |
| `make help` | List every target. |

While writing, `make livehtml` is the one to leave running.

## Quality gates

CI runs all of these, and so should you before opening a pull request.

| Command | What it checks |
| --- | --- |
| `make html` | The build must produce **zero warnings**. |
| `make linkcheckbroken` | Every link resolves. |
| `make vale` | Spelling, grammar, and Microsoft-style prose. Fix **errors**; warnings and suggestions are advisory. |
| `make doctest` | Any `doctest` blocks still produce what they claim. |
| `make test` | All of the above, from a clean build. |

Vale checks `docs/docs/**/*.md` only, so this file is not linted.

A word Vale does not know goes in `styles/config/vocabularies/Base/accept.txt`, one regular expression per line.
Add a term there only when it is genuinely a term — a misspelling is not a vocabulary gap.

## How the documentation is wired to the code

Two parts of the documentation are generated, and neither should be edited by hand.

**The Python API reference** under `docs/reference/api/` is `automodule` and nothing else.
It renders the docstrings in `backend/src/collective/multiworkflow/`, so the docstrings are where an API description belongs.
`pyproject.toml` installs the backend package as an **editable** dependency, which is what lets autodoc follow the working tree instead of a stale snapshot.

**The REST API examples** in `docs/reference/rest-api.md` are the `.req` and `.resp` files under `backend/tests/docs/http-examples/`, written by the backend test suite.
Regenerate them with `uv run pytest tests/docs` from the `backend` directory.
A payload that changes shape therefore fails the backend suite rather than quietly outdating this documentation.

## Writing conventions

- **One sentence per line.** No sentence is ever broken across lines, and no line ever holds two.
  It keeps diffs readable and lets a reviewer comment on a single sentence.
- **Sentence case headings**, and filenames with dashes rather than underscores.
- **American English**, active voice, imperative mood for instructions.
- **`html_meta` frontmatter on every page**, with `description` and `property=og:description` identical.
- **A label above every H1**, named `<section>-<slug>` — `concepts-state-variables`, `howto-search-by-workflow-state` — so other pages can cross-reference it.
- **One page owns each fact.** Everything else links to it. Duplicated facts drift apart.

Admonitions are a tool of attention: one or two per page at most.
A `note` that restates the paragraph above it should be deleted.

These follow [Plone's guide for documentation authors](https://6.docs.plone.org/contributing/documentation/authors.html), which is the authority when this file is silent.

## Adding a page

1. Decide the quadrant.
   Is the reader learning, doing, looking something up, or trying to understand? That answer is the directory.
2. Create the file with dashes in its name, and add it to the section `index.md` toctree.
3. Write the frontmatter, the label, and the H1.
4. Run `make test` before committing.

## Publishing

The site is deployed to GitHub Pages on every push to `main` that touches the documentation or the frontend.

The documentation is published at the root, and Storybook under `/storybook/`, as one artifact — see `.github/workflows/tmp-docs-publish.yml`.
Both halves are rebuilt together on purpose: deploying one without the other would let the two drift apart.

> [!NOTE]
> `make clean` removes the build directory **and** the virtual environment.
> Use it when dependencies change; the next command reinstalls everything.

## Credits and acknowledgements 🙏

Generated using [Cookieplone (2.0.0b3)](https://github.com/plone/cookieplone) and [cookieplone-templates (61a8f90)](https://github.com/plone/cookieplone-templates/commit/61a8f90e5408ce0a5337e3fdf6723369a4864ee8) on 2026-08-07 16:01:41.322560. A special thanks to all contributors and supporters!
