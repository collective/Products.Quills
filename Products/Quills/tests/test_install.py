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

PloneTestCase.installProduct("Quills")
PloneTestCase.setupPloneSite()
PORTAL_URL="http://nohost/plone"

class TestInstall(PloneTestCase.FunctionalTestCase):
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

    def afterSetUp(self):
        """Setup test enviroment. Will be executed before every test-case.
        """
        self.browser = Browser()
        self.browser.addHeader('Authorization',
                               'Basic %s:%s' % (PloneTestCase.default_user,
                                                PloneTestCase.default_password))
        self.login()
        self.setRoles(('Manager',))

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
   

    def install_ttw(self):
        """Install the product with the Quickinstaller Control Panel.
        """
        cpLabel = self.productControlPanelLabel()
        productName = self.productQuickInstallerName()
        # Go to the control panel, select and install the product there.
        browser = self.browser
        browser.open(PORTAL_URL + '/prefs_install_products_form')
        form = browser.getForm(action=PORTAL_URL + 
                                   '/portal_quickinstaller/installProducts')
        form.getControl(label=cpLabel).selected = True

        # A bug in zope.testbrowser (Launchpad #98437) will cause "submit"
        # to throw a nasty looking exception, because the Quickinstaller
        # expectsto get a correct HTTP referrer, but the testbrowser always
        # sends'localhost'. It will be taken for a relative URL, where it is
        # pure nonsense. Once this bug is solved, the try-except-cause may 
        # safely go away.
        from urllib2 import HTTPError
        try:
            form.submit('Install')
        except HTTPError: 
            # redirect manually
            browser.open(PORTAL_URL + '/prefs_install_products_form')
        
        # Now the Control Panel should show it as installed.
        form = browser.getForm(action=PORTAL_URL +
    	                              '/portal_quickinstaller$')
        self.assertTrue(form.getControl(label=cpLabel) is not None)
        
        # And the Quickinstaller should report so too.
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(quickInstaller.isProductInstalled(productName))


    def uninstall_ttw(self):
        """ Uninstall the product using the Quickinstaller control panel.
        """
        cpLabel = self.productControlPanelLabel()
        productName = self.productQuickInstallerName()
        # Go to the control panel, select and uninstall the product there.
        browser = self.browser
        browser.open(PORTAL_URL + '/prefs_install_products_form')
        form = browser.getForm(action=PORTAL_URL + 
                                   '/portal_quickinstaller$')
        form.getControl(label=cpLabel).selected = True
        
        # See install_ttw.
        from urllib2 import HTTPError
        try:
            form.submit('Uninstall')
        except HTTPError: 
            # redirect manually
            browser.open(PORTAL_URL + '/prefs_install_products_form')
        
        # Now the Control Panel should show it as installable.
        form = browser.getForm(action=PORTAL_URL + 
    	                              '/portal_quickinstaller/installProducts')
        self.assertTrue(form.getControl(label=cpLabel) is not None)
        
        # And the Quickinstaller should report it as not installed.
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(not quickInstaller.isProductInstalled(productName))


    def install_by_quickinstaller_tool(self):
        """Install the product, using the quickinstaller API.
        """
        productName = self.productQuickInstallerName()
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue( not quickInstaller.isProductInstalled(productName))
        quickInstaller.installProduct(productName)
        self.assertTrue( quickInstaller.isProductInstalled(productName) )


    def uninstall_by_quickinstaller_tool(self):
        """Uninstall the product, using the quickinstaller API.
        """
        productName = self.productQuickInstallerName()
        quickInstaller = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue( quickInstaller.isProductInstalled(productName) )
        quickInstaller.uninstallProducts( (productName,) )
        self.assertTrue( not quickInstaller.isProductInstalled(productName) )


    def install_by_generic_setup(self):
        """Install the product, using a Generic Setup extensio profile.
        """
        extensionProfile = self.productExtensionProfile()
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
        self.browser.open(PORTAL_URL)
        self.assertTrue( self.browser.getLink(id="weblog") is not None )


    def test_install_ttw(self):
        """ Test that the product installation actually gets us an usable
        product. Use the quickinstaller control panel web page for that.
        """
        self.install_ttw()
        self.product_is_usable()

        
    def test_install_by_quickinstaller_tool(self):
        """ Test that the product installation actually gets us an usable
        product. Uses the quickinstaller tool API.
        """
        self.install_by_quickinstaller_tool()
        self.product_is_usable()


    def test_install_by_generic_setup(self):
        """ Test that the product installation actually gets us an usable
        product. Uses a generic setup extension profile.
        """
        self.install_by_generic_setup()
        self.product_is_usable()


    def test_uninstall_ttw(self):
        """ Test that after uninstalling the product it can no longer be used.
        Use the quickinstaller control panel web page for that.
        """
        self.install_ttw()
        self.uninstall_ttw()
        # The portal type "Weblog" should no longer be available for adding.
        from mechanize import LinkNotFoundError
        self.browser.open(PORTAL_URL)
        self.assertRaises( LinkNotFoundError, self.browser.getLink,
                           id="weblog" )


    def test_uninstall_by_quickinstaller_tool(self):
        """ Test that after uninstalling the product it can no longer be used.
        Use the quickinstaller tool API.
        """
        self.install_by_quickinstaller_tool()
        self.uninstall_by_quickinstaller_tool()

        # The portal type "Weblog" should no longer be available for adding.
        from mechanize import LinkNotFoundError
        self.browser.open(PORTAL_URL)
        self.assertRaises( LinkNotFoundError, self.browser.getLink,
                           id="weblog" )


def test_suite():
    suite = unittest.TestSuite( unittest.makeSuite(TestInstall))
    suite.layer = PloneSite
    return suite
