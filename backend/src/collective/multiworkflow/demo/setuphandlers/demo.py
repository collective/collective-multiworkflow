from collective.multiworkflow import logger
from pathlib import Path
from plone import api

# attr-defined: plone-stubs ships no stubs for plone.exportimport, so mypy
# cannot see this submodule. The import resolves fine at runtime.
from plone.exportimport import importers  # type: ignore[attr-defined]
from Products.GenericSetup.tool import SetupTool


EXAMPLE_CONTENT_FOLDER = Path(__file__).parent / "examplecontent"


def create_example_content(portal_setup: SetupTool):
    """Import content available at the examplecontent folder."""
    portal = api.portal.get()
    importer = importers.get_importer(portal)
    for line in importer.import_site(EXAMPLE_CONTENT_FOLDER):
        logger.info(line)
    # No reindex here: importing an object's workflow history leaves the
    # additional workflow's catalog entry stale, and that is fixed for every
    # importer at once in collective.multiworkflow.exportimport rather than
    # once per setup handler.
