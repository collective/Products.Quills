"""
$Id$
"""

#import os, sys
#if __name__ == "__main__":
#    execfile(os.path.join(sys.path[0], "framework.py"))

from Products.CMFCore.utils import getToolByName
from base import QuillsTestCase

class TestWeblog(QuillsTestCase):

    def afterSetUp(self):
        self.login()
        self.setRoles(["Manager"])
        self.folder.invokeFactory("Weblog", id="weblog", title="Test Weblog")
        self.weblog = getattr(self.folder, "weblog")
        self.weblog.processForm()
        self.weblog.invokeFactory('WeblogEntry', id='test-entry',
                title="Test Entry")
        entry = self.weblog['test-entry']
        subjects = ['Keyword1', 'keyword2']
        entry.setSubject(subjects)
        # Ack, weblog.getTopics relies on a catalog query...
        entry.reindexObject()
        # We'll use this next folder to make sure topic images don't get
        # accidentally acquired
        self.folder.invokeFactory("Folder",
                                  id="Keyword1",
                                  title="Folder or Keyword1")

    def testId(self):
        self.assertEquals(self.weblog.getId(), "weblog")

    def testTitle(self):
        self.assertEquals(self.weblog.getTitle(), "Test Weblog")

    def testTopicImageFolderCreation(self):
        # Test the CREATE_TOPIC_IMAGES_FOLDERS toggle
        from Products.Quills import config
        self.failUnless( hasattr(self.weblog, config.TOPIC_IMAGE_FOLDER_ID) )
        config.CREATE_TOPIC_IMAGES_FOLDERS = False
        self.folder.invokeFactory("Weblog", id="weblog2", title="Test Weblog2")
        weblog2 = getattr(self.folder, "weblog2")
        weblog2.processForm()
        self.failIf( hasattr(weblog2, 'topic_images') )
        # Clean up after ourselves, just in case...
        config.CREATE_TOPIC_IMAGES_FOLDERS = True

    def testUploadFolderCreation(self):
        # Test the CREATE_UPLOAD_FOLDERS toggle
        from Products.Quills import config
        self.failUnless( hasattr(self.weblog, config.UPLOAD_FOLDER_ID) )
        config.CREATE_UPLOAD_FOLDERS = False
        self.folder.invokeFactory("Weblog", id="weblog2", title="Test Weblog2")
        weblog2 = getattr(self.folder, "weblog2")
        weblog2.processForm()
        self.failIf( hasattr(weblog2, 'uploads') )
        # Clean up after ourselves, just in case...
        config.CREATE_UPLOAD_FOLDERS = True

    def testGetTopics(self):
        self.failUnless(len(self.weblog.getTopics()) == 2)
        # Make sure we only get WeblogTopics back
        topic_ids = [topic.getId() for topic in self.weblog.getTopics()]
        # assertEquals cares about the order of keywords in the list!
        topic_ids.sort()
        subjects = ['Keyword1', 'keyword2']
        subjects.sort()
        self.assertEquals(topic_ids, subjects)

    def testTopicImageHandling(self):
        topic = self.weblog.getTopicById('Keyword1')
        topicimage = topic.getImage()
        # topicimage should be None, definitely not the folder that we
        # added in the setup with the id of 'Keyword1'!
        self.failUnless(topicimage is None)

    def testInterface(self):
        from quills.core.interfaces import IWeblog
        self.failUnless(IWeblog.providedBy(self.weblog))

    def _viewSortWeblogEntriesToDates(self):
        """Helper calling setWeblogEntriesToDates of the weblog view."""
        from Products.CMFPlone import Batch
        from zope.component import getMultiAdapter
        entries = self.weblog.getEntries()
        batch = Batch(entries, 10, 0, orphan=1)
        view = getMultiAdapter((self.weblog,  self.app.REQUEST),
                               name='weblog_view')
        return view.sortWeblogEntriesToDates(batch);

    def testOneStateWorkflowBug(self):
        """Test for issue #126: Entries without effective date break the blog.

           The most prominent case in which this happens is when using the
           one_state_workflow, because the effective date gets set through
           the web when the first workflow state change is triggered; which
           never happens for this workflow.
        """
        # Set the one_state_workflow for weblog entries
        wtool = getToolByName(self.getPortal(), 'portal_workflow')
        if not 'one_state_workflow' in wtool.listWorkflows():
            return
        org_entry_wf = wtool.getChainForPortalType('Weblog Entry')
        wtool.setChainForPortalTypes(('WeblogEntry',),('one_state_workflow',))
        self.assertEqual( wtool.getChainForPortalType('WeblogEntry'),
                         ('one_state_workflow',) )

        # Add another entry
        self.weblog.addEntry("No effective Date", "No description", "Nothing")
        # Update the portal catalog to reflect the new review state.
        catalog = getToolByName(self.getPortal(), 'portal_catalog')
        catalog.clearFindAndRebuild()

        self.assert_(self._viewSortWeblogEntriesToDates())

        # Undo Workflow changes
        wtool.setChainForPortalTypes(('Weblog Entry',),org_entry_wf)
        catalog.clearFindAndRebuild()

    def testNoEffectiveDateBug(self):
        """Test for issue #126: Entries without effective date break the blog.

           This test-case is more general than testOneStateWorkflowBug above,
           but less realistic. It unsets the effective date of an entry
           by force.
        """
        entry = self.weblog.addEntry("No effective Date",
                                     "No description", "Nothing")
        entry.publish()
        entry.setEffectiveDate(None)
        self.assertEqual(entry.getField('effectiveDate').get(entry), None)
        entry.reindexObject()
        self.assert_(self._viewSortWeblogEntriesToDates(),)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWeblog))
    return suite

#if __name__ == '__main__':
#    framework()
