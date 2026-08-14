from plone.base.interfaces.installable import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "collective.multiworkflow:uninstall",
            "collective.multiworkflow.demo:demo",
            "collective.multiworkflow.demo:content",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return [
            "collective.multiworkflow.demo",
            "collective.multiworkflow.upgrades",
        ]
