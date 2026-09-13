"""Generation of the HTTP examples the REST API reference renders.

``docs/docs/reference/rest-api.md`` does not hand-write its requests and
responses: it includes the ``.req`` / ``.resp`` pairs this package writes, the
way ``plone.restapi`` does. A payload that changes shape therefore either
updates the documentation or fails the suite, and never drifts quietly.

The examples land in ``http-examples/`` next to this module and are committed.
Regenerate them with ``make test`` — or, on their own::

    uv run pytest tests/docs

Two properties make the output diffable rather than noisy:

- **Only a fixed set of headers is written.** Everything else varies per run,
  per machine, or per Plone version.
- **Timestamps are frozen** by :class:`plone.restapi.tests.statictime.StaticTime`,
  which the ``docs_examples`` fixture enters for the whole test. Without it,
  every ``@history`` entry would carry the wall clock and every run would
  rewrite the file.

The pages that show a workflow definition are tested differently: their XML is
held verbatim by the test module and imported with :func:`load_definition`,
exactly as the GenericSetup import step would import it.
"""

from pathlib import Path
from Products.DCWorkflow import exportimport as dcworkflow_import
from Products.DCWorkflow.exportimport import WorkflowDefinitionConfigurator
from typing import Any

import json
import re


#: Where the generated pairs are written. The documentation includes them from
#: here by relative path, exactly as ``plone.restapi``'s docs do.
EXAMPLES_DIR = Path(__file__).parent / "http-examples"

#: Request headers worth showing. Everything else is either noise or varies
#: between runs.
REQUEST_HEADERS = ("accept", "accept-language", "authorization", "content-type")

#: Response headers worth showing.
RESPONSE_HEADERS = ("content-type", "allow", "location")

#: The port ``plone.app.testing``'s WSGI server binds is not fixed, so it is
#: normalized to the one ``plone.restapi``'s own examples use.
CANONICAL_NETLOC = "localhost:55001"

#: Written with explicit newlines so a run on macOS and a run on Linux produce
#: byte-identical files.
OPEN_KWARGS: dict[str, Any] = {"newline": "\n"}


def load_definition(workflow: Any, xml: str) -> None:
    """Import a ``definition.xml`` into a workflow, as GenericSetup does.

    The workflow import step parses the file with
    ``WorkflowDefinitionConfigurator.parseWorkflowXML`` and applies the result
    with ``_initDCWorkflow``; this does the same, so a definition that loads
    here loads from a profile, and one missing a required attribute fails here
    with the error a profile import would raise.

    :param workflow: the ``DCWorkflowDefinition`` to import into.
    :param xml: the full text of the definition.
    """
    (
        _workflow_id,
        title,
        state_variable,
        initial_state,
        states,
        transitions,
        variables,
        worklists,
        permissions,
        groups,
        scripts,
        description,
        manager_bypass,
        creation_guard,
    ) = WorkflowDefinitionConfigurator(workflow).parseWorkflowXML(xml.encode("utf-8"))
    # attr-defined: plone-stubs declares the module's public names only, and
    # this private helper is the one the GenericSetup import step calls.
    dcworkflow_import._initDCWorkflow(  # type: ignore[attr-defined]
        workflow,
        title,
        description,
        manager_bypass,
        creation_guard,
        state_variable,
        initial_state,
        states,
        transitions,
        variables,
        worklists,
        permissions,
        groups,
        scripts,
        None,
    )


def normalize(value: str) -> str:
    """Replace the test server's random port with a stable one.

    :param value: text that may carry the server's host and port.
    :returns: the text with the port normalized.
    """
    return re.sub(r"localhost:\d{4,5}", CANONICAL_NETLOC, value)


def pretty_json(data: Any) -> str:
    """Serialize a payload the way the committed examples hold it.

    Sorted keys and a trailing newline, with no trailing whitespace on any
    line: an editor opening one of these files must not be able to produce a
    diff by merely saving it.

    :param data: the decoded JSON payload.
    :returns: the serialized text.
    """
    rendered = json.dumps(data, sort_keys=True, indent=4, separators=(",", ": "))
    stripped = "\n".join(line.rstrip() for line in rendered.splitlines())
    return normalize(stripped + "\n")


def save_request(name: str, response: Any) -> None:
    """Write the request that produced ``response`` as ``<name>.req``.

    :param name: base name of the example.
    :param response: the ``requests`` response whose request is written.
    """
    request = response.request
    lines = [f"{request.method} {request.path_url} HTTP/1.1"]
    for key, value in sorted(request.headers.items()):
        if key.lower() in REQUEST_HEADERS:
            lines.append(f"{key.title()}: {value}")

    body = ""
    if request.body:
        payload = request.body
        if isinstance(payload, bytes):
            payload = payload.decode("utf8")
        body = "\n" + pretty_json(json.loads(payload))

    path = EXAMPLES_DIR / f"{name}.req"
    with open(path, "w", **OPEN_KWARGS) as handle:
        handle.write(normalize("\n".join(lines)) + "\n" + body)


def save_response(name: str, response: Any) -> None:
    """Write ``response`` as ``<name>.resp``.

    :param name: base name of the example.
    :param response: the ``requests`` response to write.
    """
    lines = [f"HTTP/1.1 {response.status_code} {response.reason}"]
    content_type = ""
    for key, value in response.headers.items():
        if key.lower() in RESPONSE_HEADERS:
            lines.append(f"{key.title()}: {normalize(value)}")
            if key.lower() == "content-type":
                content_type = value

    body = ""
    if response.text:
        if content_type.startswith("application/json"):
            body = pretty_json(response.json())
        else:
            body = normalize(response.text)

    path = EXAMPLES_DIR / f"{name}.resp"
    with open(path, "w", **OPEN_KWARGS) as handle:
        handle.write("\n".join(lines) + "\n\n" + body)


def save_example(name: str, response: Any) -> Any:
    """Write both halves of one example.

    :param name: base name of the example; the documentation includes
        ``<name>.req`` and ``<name>.resp``.
    :param response: the ``requests`` response to record.
    :returns: the response, so a caller can assert on it in the same
        expression.
    """
    EXAMPLES_DIR.mkdir(exist_ok=True)
    save_request(name, response)
    save_response(name, response)
    return response
