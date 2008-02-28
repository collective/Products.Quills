"""
$Id$
"""

#import os, sys
#if __name__ == "__main__":
#    execfile(os.path.join(sys.path[0], "framework.py"))

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

    def testInitializeArchetype(self):
        # Test the CREATE_TOPIC_IMAGES_FOLDERS toggle
        self.failUnless( hasattr(self.weblog, 'topic_images') )
        from Products.Quills import config
        config.CREATE_TOPIC_IMAGES_FOLDERS = False
        self.folder.invokeFactory("Weblog", id="weblog2", title="Test Weblog2")
        weblog2 = getattr(self.folder, "weblog2")
        weblog2.processForm()
        self.failIf( hasattr(weblog2, 'topic_images') )
        # Clean up after ourselves, just in case...
        config.CREATE_TOPIC_IMAGES_FOLDERS = True

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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWeblog))
    return suite

#if __name__ == '__main__':
#    framework()
