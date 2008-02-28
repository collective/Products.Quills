"""
$Id$
"""

#import os, sys
#if __name__ == "__main__":
#    execfile(os.path.join(sys.path[0], "framework.py"))

#from Testing import ZopeTestCase
from base import QuillsTestCase

class TestWeblogEntry(QuillsTestCase):

    def afterSetUp(self):
        self.login()
        self.setRoles(["Manager"])
        self.folder.invokeFactory("Weblog", id="weblog", title="Test Weblog")
        self.weblog = getattr(self.folder, "weblog")
        self.weblog.invokeFactory("WeblogEntry", "entry")
        entry = self.weblog.entry
        entry.setTitle("Test Entry")
        self.entry = entry
        self.types_tool = self.portal.portal_types
        self.entry_type_info = self.types_tool.getTypeInfo(self.entry.portal_type)
        self.weblog_type_info = self.types_tool.getTypeInfo(self.weblog.portal_type)

    def testEntry(self):
        self.assertEquals(self.entry.getId(), "entry")
        self.assertEquals(self.entry.Title(), "Test Entry")

    def testInterface(self):
        from quills.core.interfaces import IWorkflowedWeblogEntry
        self.failUnless(IWorkflowedWeblogEntry.providedBy(self.entry))

    def testSchema(self):
        from Products.Quills.WeblogEntry import WeblogEntrySchema
        self.assertEquals(self.entry.schema, WeblogEntrySchema)

    def testTypeInfo(self):
        self.assertEquals(self.entry_type_info.title, "Weblog Entry")
        self.assertEquals(self.entry_type_info.id, 'WeblogEntry')
        self.assertEquals(self.entry_type_info.content_icon, 'weblogentry_icon.gif')
        self.assertEquals(self.entry_type_info.global_allow, False)

    def testViews(self):
        self.assertEquals(self.entry_type_info.default_view, 'weblogentry_view')
        self.assertEquals(self.entry_type_info.immediate_view, 'weblogentry_view')
        self.assertEquals(self.entry.schema['id'].widget.visible,
                          {'view': 'invisible'})
        self.assertEquals(self.weblog_type_info.default_view, 'weblog_view')
        self.assertEquals(self.weblog_type_info.immediate_view, 'weblog_view')

    def testAllowDiscussion(self):
        # By default, Quills should use the default setting for allowing
        # discussion or not from the portal_types tool.
        # Check that the schema default is correct
        self.assertEquals(self.entry.schema['allowDiscussion'].default,
                          None)
        # Check that the actual instance attribute is also correct
        allow_discussion = getattr(self.entry.aq_explicit,
                                   'allow_discussion',
                                   None)
        self.failUnlessEqual(allow_discussion, None)

    def testMimeType(self):
        """
        by default Quills should return the sysem default for entries that haven't
        specified a type explicitly."""
        self.assertEquals(self.entry.text.getContentType(), self.entry.getMimeType())
        # if we specify a format explicitly, this should be honoured:
        self.weblog.addEntry("Foo", "Bar", "<p>23</p>", mimetype="text/html")    
        self.assertEquals("text/html", self.weblog.foo.getMimeType())
        self.weblog.addEntry("Bar", "Foo", "_42_", mimetype="text/x-web-textile")    
        self.assertEquals("text/x-web-textile", self.weblog.bar.getMimeType())
        # it is also possible to modify an existing entries type when editing it
        self.weblog.foo.edit("Foobar", "Bar", "23", [], mimetype='text/plain')
        self.assertEquals("text/plain", self.weblog.foo.getMimeType())
        # when editing w/o specifying a mimetype, the type remains unchanged:
        self.weblog.foo.edit("Foobar", "Bar", "42", [],)
        self.assertEquals("text/plain", self.weblog.foo.getMimeType())

    def testEntryCategories(self):
        entry = getattr(self.weblog, "entry")
        topics = entry.getTopics()
        self.failUnlessEqual(topics, [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWeblogEntry))
    return suite

#if __name__ == '__main__':
#    framework()
