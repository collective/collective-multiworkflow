"""Serializers for content with additional workflows.

Importing this subpackage applies the content serializer patch in
:mod:`collective.multiworkflow.restapi.serializer.dxcontent`. Including its
ZCML imports it.
"""

from .dxcontent import apply_patch


apply_patch()
