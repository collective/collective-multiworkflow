"""Summary serializer metadata for listings.

Adds the ``workflow_states`` catalog column to every ``ISerializeToJsonSummary``
payload, so a listing can show each item's state in every workflow of its chain
without one request per item.
"""

from plone.restapi.interfaces import IJSONSummarySerializerMetadata
from zope.interface import implementer


@implementer(IJSONSummarySerializerMetadata)
class JSONSummarySerializerMetadata:
    """Additional metadata to be exposed on listings."""

    def default_metadata_fields(self) -> set[str]:
        """Name the catalog columns to add to every summary.

        :returns: The set of extra field names.
        """
        return {"workflow_states"}
