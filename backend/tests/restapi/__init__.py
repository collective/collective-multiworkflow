"""Tests for the REST API extensions.

Covers the ``@workflow`` and ``@history`` endpoints, and ``workflow_states`` in
the content and summary serializations.

Values every subpackage needs live in the parent package. The ones below are
only needed here: content that exercises each of `plone.restapi`'s
``SerializeToJson`` classes on a site with ``plone.volto`` installed, where
``Document`` is folderish and ``Folder`` and ``Collection`` are not globally
addable.
"""

#: A non-folderish item, serialized by ``SerializeToJson`` itself.
PLAIN_LINK = {
    "type": "Link",
    "id": "plain-link",
    "title": "A Plain Link",
    "remoteUrl": "https://plone.org",
}

#: A collection, serialized by ``SerializeCollectionToJson``. Not creatable
#: through the ``portal`` marker, see the ``plain_collection`` fixture.
PLAIN_COLLECTION = {
    "type": "Collection",
    "id": "plain-collection",
    "title": "A Plain Collection",
}
