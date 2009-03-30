"""
Test install/uninstall of the product.

:Authors: - Jan Hackel <plonecode@hackel.name>

$Id$
"""

__docformat__ = "reStructuredText"

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite
from Testing import ZopeTestCase
from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName
import unittest

ZopeTestCase.installProduct("Quills")
PloneTestCase.setupPloneSite()

class TestInstall(PloneTestCase.FunctionalTestCase):
    """ Provide functionality needed across the test cases.
    """

    def afterSetUp(self):
        self.browser = Browser()
        self.browser.addHeader('Authorization',
                               'Basic %s:%s' % (PloneTestCase.default_user,
                                                PloneTestCase.default_password))
        self.login()
        self.setRoles(('Manager',))


    def install_ttw(self, productName):
        """Install the product with the Quickinstaller Control Panel.
        """
        # Go to the control panel, select and install the product there.
        browser = self.browser
        browser.open('http://nohost/plone/prefs_install_products_form')
        form = browser.getForm(action='http://nohost/plone/'
                                   'portal_quickinstaller/installProducts')
        form.getControl(label=productName).selected = True

        # A bug in zope.testbrowser (Launchpad #98437) will cause the submit
        # to throw a nasty looking exception, because the Quickinstaller
        # expectsto get a correct HTTP referrer, but the testbrowser always
        # sends'localhost'. It will be take for a relative URL, where it is
        # pure nonesense. Once this bug is solve the try-except-cause may 
        # safely go away.
        from urllib2 import HTTPError
        try:
            form.submit('Install')
        except HTTPError: 
            # redirect manually
            browser.open('http://nohost/plone/prefs_install_products_form')
        
        # Now the Control Panel should show it as installed.
        form = browser.getForm(action='http://nohost/plone/'
    	                              'portal_quickinstaller$')
        self.assertTrue( form.getControl(label=productName) is not None)
        
        # And the Quickinstaller should report so too.
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(quickInstaller.isProductInstalled(productName))


    def uninstall_ttw(self, productName):
        """ Uninstall the product using the Quickinstaller control panel.
        """
        # Go to the control panel, select and uninstall the product there.
        browser = self.browser
        browser.open('http://nohost/plone/prefs_install_products_form')
        form = browser.getForm(action='http://nohost/plone/'
                                   'portal_quickinstaller$')
        form.getControl(label=productName).selected = True

        # A bug in zope.testbrowser (Launchpad #98437) will cause the submit
        # to throw a nasty looking exception, because the Quickinstaller
        # expectsto get a correct HTTP referrer, but the testbrowser always
        # sends'localhost'. It will be take for a relative URL, where it is
        # pure nonesense. Once this bug is solve the try-except-cause may 
        # safely go away.
        from urllib2 import HTTPError
        try:
            form.submit('Uninstall')
        except HTTPError: 
            # redirect manually
            browser.open('http://nohost/plone/prefs_install_products_form')
        
        # Now the Control Panel should show it as installable.
        form = browser.getForm(action='http://nohost/plone/'
    	                              'portal_quickinstaller/installProducts')
        self.assertTrue( form.getControl(label=productName) is not None)
        
        # And the Quickinstaller should report it as not installed.
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(not quickInstaller.isProductInstalled(productName))


    def install_by_quickinstaller_tool(self, productName):
        """Install the product, using the quickinstaller API."""
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue( not quickInstaller.isProductInstalled(productName) )
        quickInstaller.installProduct(productName)
        self.assertTrue( quickInstaller.isProductInstalled(productName) )


    def uninstall_by_quickinstaller_tool(self, productName):
        """Uninstall the product, using the quickinstaller API."""
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue( quickInstaller.isProductInstalled(productName) )
        quickInstaller.uninstallProducts( (productName,) )
        self.assertTrue( not quickInstaller.isProductInstalled(productName) )


    def install_by_generic_setup(self, extensionProfile):
        """Install the product, using a Generic Setup extensio profile."""
        gs = getToolByName(self.portal, 'portal_setup')
        self.assertEqual(gs.getBaselineContextID(),
                         "profile-Products.CMFPlone:plone")
        # gs.setBaselineContext("profile-Products.CMFPlone:plone")
        gs.runAllImportStepsFromProfile("profile-%s" % (extensionProfile,))

        
    def product_is_usable(self):
        """ Check if the product is usable.
        """
        # The portal type "Weblog" should now be available for adding.
        # Let's see if we have that option for the portal object.
        self.browser.open('http://nohost/plone/')
        self.assertTrue( self.browser.getLink(id="weblog") is not None )


    def test_install_ttw(self):
        """ Test that the product installation actually gets us an usable
        product. Use the quickinstaller control panel web page for that.
        """
        self.install_ttw("Quills")
        self.product_is_usable()

        
    def test_install_by_quickinstaller_tool(self):
        """ Test that the product installation actually gets us an usable
        product. Uses the quickinstaller tool API.
        """
        
        self.install_by_quickinstaller_tool("Quills")
        self.product_is_usable()


    def test_install_by_generic_setup(self):
        """ Test that the product installation actually gets us an usable
        product. Uses a generic setup extension profile.
        """
        self.install_by_generic_setup("Products.Quills:default")
        self.product_is_usable()


    def test_uninstall_ttw(self):
        """ Test that after uninstalling the product it can no longer be used.
        Use the quickinstaller control panel web page for that.
        """
        self.install_ttw("Quills")
        self.uninstall_ttw("Quills")
        # The portal type "Weblog" should no longer be available for adding.
        from mechanize import LinkNotFoundError
        self.browser.open('http://nohost/plone/')
        self.assertRaises( LinkNotFoundError, self.browser.getLink,
                           id="weblog" )


    def test_uninstall_by_quickinstaller_tool(self):
        """ Test that after uninstalling the product it can no longer be used.
        Use the quickinstaller tool API.
        """
        self.install_by_quickinstaller_tool("Quills")
        self.uninstall_by_quickinstaller_tool("Quills")

        # The portal type "Weblog" should no longer be available for adding.
        from mechanize import LinkNotFoundError
        self.browser.open('http://nohost/plone/')
        self.assertRaises( LinkNotFoundError, self.browser.getLink,
                           id="weblog" )


def test_suite():
    suite = unittest.TestSuite( unittest.makeSuite(TestInstall))
    suite.layer = PloneSite
    return suite
