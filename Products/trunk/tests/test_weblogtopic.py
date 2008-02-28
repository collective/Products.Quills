"""
$Id$
"""

from base import QuillsTestCase

class TestWeblogTopic(QuillsTestCase):

    def afterSetUp(self):
        self.setRoles(["Manager"])
        self.folder.invokeFactory("Weblog", id="weblog", title="Test Weblog")
        self.weblog = getattr(self.folder, "weblog")

    def testTopic(self):
        self.failUnless(len(self.weblog.getTopics()) == 0)
        # Lots of this testing now found in test_quills.TestWeblog.testGetTopics


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWeblogTopic))
    return suite
