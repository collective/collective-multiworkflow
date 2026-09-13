"""The subscriber ``how-to-guides/react-to-another-workflow.md`` shows, verbatim.

It lives in a module of its own so that the ZCML registering it in the tests is
the ZCML the how-to shows, down to the relative dotted name of the handler.
Left unannotated for the same reason: the page shows it exactly as it is here.
"""

from collective.multiworkflow import api as mw_api


def activate_membership_on_publish(obj, event):
    """Activate the membership of content as soon as it is published."""
    if event.workflow.getId() != "simple_publication_workflow":
        return
    if event.new_state.getId() != "published":
        return
    if mw_api.get_state(obj, workflow_id="foundation_member_workflow") != "pending":
        return
    mw_api.transition(obj, "activate", workflow_id="foundation_member_workflow")
