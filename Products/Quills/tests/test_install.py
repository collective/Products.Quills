"""
Test install/uninstall of the product.

:Authors: - Jan Hackel <plonecode@hackel.name>

$Id$
"""

__docformat__ = "reStructuredText"

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite
from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName
import unittest
from quills.app.tests import install_testbase as base

PloneTestCase.installProduct("fatsyndication")
PloneTestCase.installProduct("Quills")
PloneTestCase.setupPloneSite()
PORTAL_URL="http://nohost/plone"

class TestInstall(base.TestInstall):
    """ Provide functionality needed across the test cases.
    """

    def productExtensionProfile(self):
        """Return the Generic Setup extension profile of the product
        to be tested.
        """
        return "Products.Quills:default"

    def productControlPanelLabel(self):
        """Return label by which the checkbox that selects the
        product to be tested in the Quickinstaller control panel.
        """
        return "Quills"

    def productQuickInstallerName(self):
        """Return the name of the product to be tested. Must be fitting
        for the Quickinstaller API.
        """
        return "Quills"

    def product_is_usable(self):
        """ Check if the product is usable.
        """
        # The portal type "Weblog" should now be available for adding.
        # Let's see if we have that option for the portal object.
        self.browser.open(PORTAL_URL)
        self.assertTrue( self.browser.getLink(id="weblog") is not None )

    def afterSetUp(self):
        """Setup test enviroment. Will be executed before every test-case.
        """
        super(TestInstall,self).afterSetUp()
        # When this test-suite is run together with the other test-cases
        # we might get a plone instance where Quills is already installed.
        # Now, having to uninstall this package in a test that is supposed
        # to test install/uninstall is rather doubious... Setting up
        # a Plone Site with a custom id would be a solution, but that
        # code is broken (Plone ticket #9078).
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        if quickInstaller.isProductInstalled('Quills'):
            quickInstaller.uninstallProducts( ("Quills",) )

        if quickInstaller.isProductInstalled('Products.Quills'):
            quickInstaller.uninstallProducts( ("Products.Quills",) )
        


def test_suite():
    suite = unittest.TestSuite( unittest.makeSuite(TestInstall))
    suite.layer = PloneSite
    return suite
