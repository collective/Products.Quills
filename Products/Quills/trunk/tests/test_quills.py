"""
$Id$
"""

#import os, sys
#if __name__ == "__main__":
#    execfile(os.path.join(sys.path[0], "framework.py"))

from base import QuillsTestCase

from Products.CMFCore.utils import getToolByName

class TestPortalTypes(QuillsTestCase):

    def afterSetUp(self):
        self.types = self.portal.portal_types.objectIds()

    def testPortalTypesExists(self):
        types = ("Weblog", "WeblogEntry",)
        for t in types:
            self.failUnless(t in self.types, "Type not installed: %s" % t)

    def testQuillsAllowedTypes(self):
        u"""Test the Weblog allowed content types.

        Only WeblogEntry and WeblogTopic should be available.
        """
        weblog = self.portal.portal_types.getTypeInfo('Weblog')
        self.failUnless("WeblogEntry" in weblog.allowed_content_types)


class TestFolderContainment(QuillsTestCase):

    def afterSetUp(self):
        self.login()
        self.folder.invokeFactory("Weblog", id="weblog", title="Test Weblog")

    def testQuillsContainment(self):
        """Test adding objects that we should be able to add to a Weblog."""
        self.folder.weblog.invokeFactory("WeblogEntry", id="entry")
        self.failUnless("entry" in self.folder.weblog.objectIds())

class TestSetup(QuillsTestCase):
    """check for various setup issues"""

    def testSkinLayersInstalled(self):
        self.failUnless('Quills' in self.portal.portal_skins.objectIds())

    def testDefaultPageTypes(self):
        ptool = getToolByName(self, 'portal_properties')
        default_page_types = ptool.site_properties.getProperty('default_page_types')
        self.failUnless('Weblog' in default_page_types)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalTypes))
    suite.addTest(makeSuite(TestFolderContainment))
    suite.addTest(makeSuite(TestSetup))
    return suite

#if __name__ == '__main__':
#    framework()
