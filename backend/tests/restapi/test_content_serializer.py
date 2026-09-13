"""Tests for ``workflow_states`` in the content and summary serializations.

The key is added by patching ``SerializeToJson.__call__`` on the class itself.
So the claim worth pinning is not only that one content type carries it, but
that every serializer reaching that method through ``super()`` does:
`plone.restapi`'s folder and collection serializers, and a subclass standing in
for an add-on's.
"""

from . import PLAIN_COLLECTION
from . import PLAIN_LINK
from collective.multiworkflow import api as mwapi
from collective.multiworkflow.restapi.serializer import dxcontent
from collective.multiworkflow.utils.workflow import format_state
from collective.multiworkflow.utils.workflow import formatted_workflow_states
from collective.multiworkflow.utils.workflow import WORKFLOW_STATES
from plone import api
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.collection import SerializeCollectionToJson
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from tests import flush_indexing
from tests import MEMBER_PROFILE
from tests import PLAIN_DOCUMENT
from tests import PUBLICATION_WORKFLOW
from typing import Any
from zope.component import getMultiAdapter

import pytest


def serialize(obj: Any, request: Any, **kwargs: Any) -> dict:
    """Serialize one object through its registered ``ISerializeToJson`` adapter.

    :param obj: the object to serialize.
    :param request: the request to serialize it for.
    :param kwargs: passed to the serializer, e.g. ``version``.
    :returns: the payload.
    """
    return getMultiAdapter((obj, request), ISerializeToJson)(**kwargs)


def expected_states(obj: Any) -> list[str]:
    """Build the ``workflow_states`` value an object should be serialized with.

    Built from :func:`collective.multiworkflow.api.get_states` rather than from
    the helper the patch calls, so the assertion does not merely compare that
    helper with itself.

    :param obj: the serialized object.
    :returns: one ``<workflow-id>|<state-id>`` value per workflow, in chain order.
    """
    return [
        format_state(wf_id, state) for wf_id, state in mwapi.get_states(obj).items()
    ]


class DerivedFolderSerializer(SerializeFolderToJson):
    """Stands in for an add-on's serializer derived from `plone.restapi`'s."""

    def __call__(
        self,
        version: str | None = None,
        include_items: bool = True,
        include_expansion: bool = True,
    ) -> dict:
        result = super().__call__(
            version=version,
            include_items=include_items,
            include_expansion=include_expansion,
        )
        result["derived"] = True
        return result


@pytest.fixture()
def plain_collection(portal: Any) -> Any:
    """A Collection, created past the site's add constraints.

    ``plone.volto`` sets ``global_allow`` to false on ``Collection``, so the
    ``portal`` marker — which goes through ``plone.api.content.create`` — cannot
    add one. What is under test is the serializer, not the constraint, so this
    fixture skips the check instead of changing the type's configuration.
    """
    spec = {key: value for key, value in PLAIN_COLLECTION.items() if key != "type"}
    return createContentInContainer(
        portal, PLAIN_COLLECTION["type"], checkConstraints=False, **spec
    )


class TestPatchInstallation:
    """The wrapper is in place, once, on the class `plone.restapi` registers."""

    def test_method_is_patched(self) -> None:
        """Importing the serializer subpackage wrapped the method."""
        assert (
            getattr(SerializeToJson.__call__, "patched_by", None) == dxcontent.__name__
        )

    def test_patch_is_idempotent(self) -> None:
        """Applying it twice does not wrap the wrapper."""
        patched = SerializeToJson.__call__

        dxcontent.apply_patch()

        assert SerializeToJson.__call__ is patched

    def test_original_is_reachable(self) -> None:
        """The spike reads upstream's behavior through ``__wrapped__``."""
        assert not hasattr(SerializeToJson.__call__.__wrapped__, "patched_by")


@pytest.mark.portal(
    content=[PLAIN_DOCUMENT, PLAIN_LINK, MEMBER_PROFILE],
    roles=["Manager"],
)
class TestEverySerializerCarriesTheKey:
    """Each class reaching ``SerializeToJson.__call__`` through ``super()``."""

    @pytest.fixture(autouse=True)
    def _setup(self, portal: Any, http_request: Any, plain_collection: Any) -> None:
        self.portal = portal
        self.request = http_request
        self.content = {
            PLAIN_DOCUMENT["id"]: portal[PLAIN_DOCUMENT["id"]],
            PLAIN_LINK["id"]: portal[PLAIN_LINK["id"]],
            PLAIN_COLLECTION["id"]: plain_collection,
            MEMBER_PROFILE["id"]: portal[MEMBER_PROFILE["id"]],
        }

    @pytest.mark.parametrize(
        "content_id,serializer_class",
        [
            (PLAIN_LINK["id"], SerializeToJson),
            (PLAIN_DOCUMENT["id"], SerializeFolderToJson),
            (PLAIN_COLLECTION["id"], SerializeCollectionToJson),
        ],
    )
    def test_registered_class(self, content_id: str, serializer_class: type) -> None:
        """The premise: each content type is served by the class it stands for.

        If ``plone.volto`` or `plone.restapi` change which class serves a type,
        this fails first, and the tests below stop covering what they claim to.
        """
        serializer = getMultiAdapter(
            (self.content[content_id], self.request), ISerializeToJson
        )

        assert type(serializer) is serializer_class

    @pytest.mark.parametrize(
        "content_id",
        [
            PLAIN_LINK["id"],
            PLAIN_DOCUMENT["id"],
            PLAIN_COLLECTION["id"],
            MEMBER_PROFILE["id"],
        ],
    )
    def test_registered_serializer(self, content_id: str) -> None:
        """The serializer a ``GET`` would use carries the object's states."""
        obj = self.content[content_id]

        result = serialize(obj, self.request)

        assert result[WORKFLOW_STATES] == expected_states(obj)

    def test_derived_serializer(self) -> None:
        """A subclass of ``SerializeFolderToJson`` carries the key too."""
        obj = self.content[PLAIN_DOCUMENT["id"]]

        result = DerivedFolderSerializer(obj, self.request)()

        assert result[WORKFLOW_STATES] == expected_states(obj)

    def test_derived_serializer_keeps_its_own_keys(self) -> None:
        """The patch adds to a derived payload; it does not replace it."""
        result = DerivedFolderSerializer(
            self.content[PLAIN_DOCUMENT["id"]], self.request
        )()

        assert result["derived"] is True

    @pytest.mark.parametrize(
        "content_id",
        [PLAIN_LINK["id"], PLAIN_DOCUMENT["id"], MEMBER_PROFILE["id"]],
    )
    def test_first_entry_is_review_state(self, content_id: str) -> None:
        """Entry zero agrees with the ``review_state`` of the same payload."""
        result = serialize(self.content[content_id], self.request)

        assert result[WORKFLOW_STATES][0] == format_state(
            PUBLICATION_WORKFLOW, result["review_state"]
        )

    def test_participating_content_lists_every_workflow(self) -> None:
        """Content with an additional workflow carries one value per workflow."""
        result = serialize(self.content[MEMBER_PROFILE["id"]], self.request)

        assert len(result[WORKFLOW_STATES]) == 2


@pytest.mark.portal(content=[MEMBER_PROFILE], roles=["Manager"])
class TestHistoricalVersion:
    """A historical version reads its states where core reads ``review_state``."""

    @pytest.fixture(autouse=True)
    def _setup(self, portal: Any, http_request: Any) -> None:
        profile = portal[MEMBER_PROFILE["id"]]
        repository = api.portal.get_tool("portal_repository")
        repository.save(obj=profile, comment="Snapshot")
        self.version = str(len(repository.getHistory(profile)) - 1)
        self.result = serialize(profile, http_request, version=self.version)

    def test_payload_is_the_historical_version(self) -> None:
        """The premise: the serializer really did serialize a version."""
        assert self.result["version"] == self.version

    def test_states_are_serialized(self) -> None:
        """Both workflows are described, and entry zero matches ``review_state``."""
        states = self.result[WORKFLOW_STATES]

        assert len(states) == 2
        assert states[0] == format_state(
            PUBLICATION_WORKFLOW, self.result["review_state"]
        )


@pytest.mark.portal(content=[PLAIN_DOCUMENT, MEMBER_PROFILE], roles=["Manager"])
class TestSummarySerialization:
    """Listings read the ``workflow_states`` metadata column."""

    @pytest.fixture(autouse=True)
    def _setup(self, portal: Any, http_request: Any) -> None:
        flush_indexing()
        self.portal = portal
        self.request = http_request

    @pytest.mark.parametrize(
        "content_id",
        [PLAIN_DOCUMENT["id"], MEMBER_PROFILE["id"]],
    )
    def test_brain_summary(self, content_id: str) -> None:
        """A catalog brain's summary carries the object's states."""
        obj = self.portal[content_id]
        brain = api.content.find(UID=obj.UID())[0]

        summary = getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()

        assert summary[WORKFLOW_STATES] == list(formatted_workflow_states(obj))


@pytest.mark.portal(content=[PLAIN_DOCUMENT], roles=["Manager"])
class TestOverHttp:
    """The patch is in place in a real request, not only in direct calls."""

    def test_folderish_payload(
        self, committed_portal: Any, manager_request: Any
    ) -> None:
        """``GET`` on folderish content returns the key."""
        response = manager_request.get(f"/{PLAIN_DOCUMENT['id']}")

        assert response.status_code == 200, response.text
        assert response.json()[WORKFLOW_STATES] == expected_states(
            committed_portal[PLAIN_DOCUMENT["id"]]
        )
