"""Tests for the example behavior and its demo profile.

Shared values for the package live here so test modules and ``conftest`` import
them relatively; values the whole suite needs live in the parent package.
"""

#: Configuration and example content are separate profiles. The test layer
#: applies ``collective.multiworkflow.demo:demo`` for every test; this one is
#: left to the tests that want it, because the importer behind it commits and
#: an integration layer's per-test rollback cannot undo that.
CONTENT_PROFILE = "collective.multiworkflow.demo:content"

#: Ids of the objects that profile imports.
EXAMPLE_DOCUMENT = "profiles"
EXAMPLE_PROFILE_ITEM = "ortegas"

#: Name the behavior is registered under in ``demo/configure.zcml``.
FOUNDATION_MEMBER_BEHAVIOR = "collective.multiworkflow.demo.foundation_member"
