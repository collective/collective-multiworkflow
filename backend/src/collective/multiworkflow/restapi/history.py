"""``@history`` for content with additional workflows.

`plone.restapi`'s service builds its listing from
``ContentHistoryViewlet.fullHistory()``, which reads ``review_history`` through
``WorkflowTool.getInfoFor`` without a ``wf_id``. That call returns the history
of the *first* workflow in the chain that supports the variable — always the
primary one — so an additional workflow's transitions are simply absent.

The fix is in the viewlet, not in the service: :class:`ChainHistoryViewlet`
collects every workflow's history, so core's own merge, ordering and entry
shaping apply to the whole chain unchanged. Every entry carries a
``workflow_id``: the id of the workflow that recorded the transition, or
``None`` for versioning entries, so a client can attribute an entry without
inferring anything from its shape.
"""

from datetime import datetime
from datetime import UTC
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.base import PloneMessageFactory as _
from plone.restapi.bbb import safe_text
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services.history.get import HistoryGet
from Products.CMFCore.utils import getToolByName
from typing import Any
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite


#: Variable every stock Plone workflow uses to record its history.
REVIEW_HISTORY = "review_history"


class ChainHistoryViewlet(ContentHistoryViewlet):
    """Content history covering every workflow in the object's chain."""

    def workflowHistory(self, complete: bool = True) -> list:
        """Return the history of all the object's workflows, newest first.

        Each entry is tagged with the id of the workflow that recorded it.
        Reading is per workflow, so each one's ``review_history`` info guard
        decides whether its entries are visible — on top of the blanket check
        core applies, which is preserved here.

        :param complete: when false, automatic transitions are filtered out,
            as upstream.
        :returns: entries shaped exactly like the ones core's viewlet emits,
            plus a ``workflow_id`` key.
        """
        history = super().workflowHistory(complete=complete)
        primary = self._primary_workflow_id()
        for entry in history:
            entry["workflow_id"] = primary

        history.extend(self._additional_history(primary, complete))
        return history

    def _workflows(self) -> list:
        """Return the workflows applying to this object, in chain order.

        :returns: the chain's workflow definitions.
        """
        wftool = getToolByName(self.context, "portal_workflow")
        return list(wftool.getWorkflowsFor(self.context) or [])

    def _primary_workflow_id(self) -> str | None:
        """Return the id of the workflow whose history core already reported.

        Mirrors the lookup ``WorkflowTool.getInfoFor`` performs with no
        ``wf_id``: the first workflow in the chain that supports the variable.

        :returns: the workflow id, or ``None`` if no workflow records history.
        """
        for workflow in self._workflows():
            if workflow.isInfoSupported(self.context, REVIEW_HISTORY):
                return workflow.getId()
        return None

    def _additional_history(self, primary: str | None, complete: bool) -> list:
        """Return entries for every workflow core's viewlet skipped.

        :param primary: id of the workflow core already reported, if any.
        :param complete: when false, automatic transitions are filtered out.
        :returns: the remaining workflows' entries, newest first.
        """
        wftool = getToolByName(self.context, "portal_workflow")

        entries = []
        for workflow in self._workflows():
            workflow_id = workflow.getId()
            if workflow_id == primary:
                continue
            if not workflow.isInfoSupported(self.context, REVIEW_HISTORY):
                continue
            # A default is required: ``review_history`` carries an info guard,
            # and a read the guard denies raises unless one is supplied.
            records = wftool.getInfoFor(
                self.context, REVIEW_HISTORY, [], wf_id=workflow_id
            )
            workflow_history = [
                self._entry(record, workflow)
                for record in records or []
                if complete or record.get("action")
            ]
            workflow_history.reverse()
            entries.extend(workflow_history)
        return entries

    def _entry(self, record: dict, workflow: Any) -> dict:
        """Turn one raw ``review_history`` record into a viewlet entry.

        Titles are resolved from the workflow's own definition rather than
        through ``getTitleForStateOnType`` / ``getTitleForTransitionOnType``,
        which look the chain up per *type* and so cannot see a workflow
        contributed by a behavior.

        :param record: one entry of the workflow's ``review_history``.
        :param workflow: the workflow definition that recorded it.
        :returns: an entry shaped like the ones core's viewlet emits.
        """
        entry = dict(record)
        entry["type"] = "workflow"
        entry["workflow_id"] = workflow.getId()
        entry["transition_title"] = self._transition_title(
            workflow, record.get("action")
        )
        entry["state_title"] = self._state_title(
            workflow, record.get(workflow.state_var, "")
        )

        actorid = record.get("actor")
        entry["actorid"] = actorid
        if actorid is None:
            # Matches how core labels a transition with no known actor.
            anonymous = _("label_anonymous_user", default="Anonymous User")
            entry["actor"] = {"username": anonymous, "fullname": anonymous}
            entry["actor_home"] = ""
        else:
            entry.update(self.getUserInfo(actorid))

        return entry

    def _transition_title(self, workflow: Any, action: str | None) -> Any:
        """Return the label for a recorded transition.

        :param workflow: the workflow that recorded it.
        :param action: the transition id, or ``None`` for the creation entry.
        :returns: the transition title, translatable.
        """
        if not action:
            # The creation entry has no action; core labels it this way too.
            return _("Create")

        transition = workflow.transitions.get(action)
        title = getattr(transition, "actbox_name", "") or getattr(
            transition, "title", ""
        )
        return title or action

    def _state_title(self, workflow: Any, state_id: str) -> Any:
        """Return the label for a state of one workflow.

        :param workflow: the workflow the state belongs to.
        :param state_id: id of the state recorded on the entry.
        :returns: the state title, translatable, falling back to the id.
        """
        state = workflow.states.get(state_id)
        title = getattr(state, "title", "") if state is not None else ""
        return title or state_id


class ChainHistoryGet(HistoryGet):
    """List the history of every workflow in the object's chain."""

    # The C901 waiver below: this method's complexity is inherited from the
    # upstream body it vendors. The two local differences are marked inline and
    # kept minimal on purpose, so splitting it up would only make the diff
    # against core harder to audit.
    def reply(self) -> Any:  # noqa: C901
        """Return the merged history, newest first.

        The body below is ``plone.restapi.services.history.get.HistoryGet``
        (10.0.2) with two deliberate differences, both marked inline: the
        viewlet class, and a ``workflow_id`` default for entries that belong to
        no workflow. It is vendored rather than post-processed because core
        sorts on the *raw* times and only then truncates them to whole seconds
        — re-sorting the shaped entries afterwards would tie, and lose the
        order of anything recorded within the same second.

        :returns: the history listing, or a serialized object when traversing
            to a specific version.
        """
        # Traverse to historical version
        if self.version:
            # ISerializeToJson declares no __call__ signature, so mypy cannot
            # see that every implementation is callable.
            serializer: Any = queryMultiAdapter(
                (self.context, self.request), ISerializeToJson
            )
            data = serializer(version=self.version)
            return data

        # Listing historical data
        # DIFFERENCE: the chain-aware viewlet, in place of core's.
        content_history_viewlet = ChainHistoryViewlet(
            self.context, self.request, None, None
        )
        # ISite declares no API of its own; the portal is an ordinary content
        # object, exactly as plone.restapi's own service assumes.
        site: Any = getSite()
        site_url = site.absolute_url()
        content_history_viewlet.navigation_root_url = site_url
        content_history_viewlet.site_url = site_url
        history = content_history_viewlet.fullHistory()
        if history is None:
            history = []

        unwanted_keys = [
            "diff_current_url",
            "diff_previous_url",
            "preview_url",
            "actor_home",
            "actorid",
            "revert_url",
            "version_id",
        ]

        for item in history:
            # DIFFERENCE: versioning entries belong to no workflow, but the key
            # is present on every entry so clients can rely on it.
            item.setdefault("workflow_id", None)

            item["actor"] = {
                "@id": "{}/@users/{}".format(site_url, item["actorid"]),
                "id": item["actorid"],
                "fullname": item["actor"].get("fullname"),
                "username": item["actor"].get("username"),
            }

            if item["type"] == "versioning":
                item["version"] = item["version_id"]
                item["@id"] = "{}/@history/{}".format(
                    self.context.absolute_url(), item["version"]
                )

                # If a revert_url is present, then CMFEditions has checked our
                # permissions.
                item["may_revert"] = bool(item.get("revert_url"))

            # Versioning entries use a timestamp,
            # workflow ISO formatted string
            if not isinstance(item["time"], str):
                item["time"] = datetime.fromtimestamp(
                    int(item["time"]), tz=UTC
                ).isoformat(timespec="seconds")

            # The create event has an empty 'action', but we like it to say
            # 'Create', alike the transition_title
            if item["action"] is None:
                item["action"] = "Create"

            # We want action, state and transition names translated
            if "state_title" in item:
                item["state_title"] = self.context.translate(
                    safe_text(item["state_title"]), context=self.request
                )

            if "transition_title" in item:
                item["transition_title"] = self.context.translate(
                    safe_text(item["transition_title"]), context=self.request
                )

            if "action" in item:
                item["action"] = self.context.translate(
                    safe_text(item["action"]), context=self.request
                )

            # clean up
            for key in unwanted_keys:
                if key in item:
                    del item[key]

        return json_compatible(history)
