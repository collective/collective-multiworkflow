"""A worked example of an additional workflow.

This subpackage is the only thing in ``collective.multiworkflow`` that touches a
site's content types, and it is kept separate so that installing the add-on does
not: the root ``configure.zcml`` never includes it, so neither the
``foundation_member`` behavior nor its ``demo`` profile exists in a plain
installation.

A site that wants the example loads this package's ZCML explicitly — as this
repository's ``instance.yaml`` does for local development — and then installs
the ``collective.multiworkflow.demo:demo`` profile.
"""
