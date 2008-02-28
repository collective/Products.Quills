"""
$Id$
"""

from Products.CMFCore.utils import getToolByName
from Products.Quills.migrations import quills09to15
from base import QuillsTestCase
from quills.trackback.interfaces import ITrackbackOutManager
from StringIO import StringIO

class TestMigration09_15(QuillsTestCase):

    def afterSetUp(self):
        self.login()
        self.setRoles(["Manager"])
        self.portal.invokeFactory("Weblog", id="weblog", title="Test Weblog")
        self.weblog = getattr(self.portal, "weblog")
        self.portal.invokeFactory("Weblog",
                                  id="weblog_non_ascii",
                                  title="\xd0\x91\xd0\xbb\xd0\xbe\xd0\xb3")
        self.weblog_non_ascii = getattr(self.portal, "weblog_non_ascii")
        self.weblog.invokeFactory(
            'WeblogEntry',
            id='testentry',
            title='Testentry',
            text='Sample text')
        self.entry = self.weblog.testentry
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.catalog.reindexObject(self.entry)
        self.out = StringIO()
        self.migration = quills09to15.Migration(site=self.portal,
                                                out=self.out)
        # Remove topic_images
        if hasattr(self.weblog, 'topic_images'):
            self.weblog.manage_delObjects(ids=['topic_images'])
        # Add an index that doesn't get used anymore
        index = 'getEntryCategories'
        if index not in self.catalog.indexes():
            self.catalog.addIndex(index, 'FieldIndex')
        # transaction to allow copy/move 
        from transaction import savepoint; savepoint()

    def test_migrateWeblog(self):
         pass

    def test_migrateWeblogEntry(self):
        pass

    def test_migrateTrackbacksForEntry(self):
        # Modify the entry to have the old trackback attribute.
        existingURLs = ['http://sam.pl/e', 
                        'http://example.org/reutel']
        existingURLs.sort()
        self.entry.trackbackURLs = existingURLs
        # Migrate and check the results.
        self.migration.migrateTrackbacksForEntry(self.entry)
        tbim = ITrackbackOutManager(self.entry)
        # We're not published, so check for the urls we still have to
        # ping.
        results = list(tbim.getURLsToPing())
        results.sort()
        self.assertEquals(existingURLs, results)
        # The trackbackURLS attribute should be gone.
        self.assertEquals(getattr(self.entry, 'trackbackURLs',
                                   'way of the dodo'),
                          'way of the dodo')
        # Migrate again, results should be the same.
        self.migration.migrateTrackbacksForEntry(self.entry)
        results = list(tbim.getURLsToPing())
        results.sort()
        self.assertEquals(existingURLs, results)

    def test_migrateTrackbacksForEntry_published(self):
        # Disabled because publishing the item broke the unittesting
        # mechanism somehow.

        # Modify the entry to have the old trackback attribute.
        existingURLs = ['http://sam.pl/e', 
                        'http://example.org/reutel']
        existingURLs.sort()
        self.entry.trackbackURLs = existingURLs
        # Publish the entry.
        wftool = getToolByName(self.entry, 'portal_workflow')
        wftool.doActionFor(self.entry, 'publish')
        # Migrate and check the results.
        self.migration.migrateTrackbacksForEntry(self.entry)
        tbim = ITrackbackOutManager(self.entry)
        # Now we need to search for the pinged URLs.
        results = list(tbim.getPingedURLs())
        results.sort()
        self.assertEquals(existingURLs, results)
        # The trackbackURLS attribute should be gone.
        self.assertEquals(getattr(self.entry, 'trackbackURLs',
                                   'way of the dodo'),
                          'way of the dodo')
        # Migrate again, results should be the same.
        self.migration.migrateTrackbacksForEntry(self.entry)
        tbim = ITrackbackOutManager(self.entry)
        results = list(tbim.getPingedURLs())
        results.sort()
        self.assertEquals(existingURLs, results)

    def test_migrateCategoriesForEntry(self):
        # Modify the entry to have categories.
        categories = ['sample', 'category']
        self.entry.entryCategories = categories
        # Add an existing subject for good measure.
        self.entry.setSubject(['existing'])
        expected = ['sample', 'category', 'existing']
        expected.sort()
        # Migrate and check the results.
        self.migration.migrateCategoriesForEntry(self.entry)
        subjects = list(self.entry.Subject())
        subjects.sort()
        self.assertEquals(subjects, expected)
        # The entryCategories attribute should be gone.
        self.assertEquals(getattr(self.entry, 'entryCategories',
                                  'way of the dodo'),
                          'way of the dodo')
        # Migrate again, results should be the same.
        self.migration.migrateCategoriesForEntry(self.entry)
        subjects = list(self.entry.Subject())
        subjects.sort()
        self.assertEquals(subjects, expected)
        
    def test_migrateWeblogTopics(self):
        self.migration.migrateWeblogTopics(self.weblog)
        self.failUnless(hasattr(self.weblog, 'topic_images'))
        # And we call it again, which should be possible.
        self.migration.migrateWeblogTopics(self.weblog)
        self.failUnless(hasattr(self.weblog, 'topic_images'))
        # The type=WeblogTopic migration is hard to test, as there's
        # no WeblogTopic contenttype anymore.

    def test_removeEntryCategoriesIndex(self):
        index = 'getEntryCategories'
        self.migration.removeEntryCategoriesIndex()
        self.failUnless(index not in self.catalog.indexes())
        # Call it again, which should be possible.
        self.migration.removeEntryCategoriesIndex()
        self.failUnless(index not in self.catalog.indexes())

    def test_nonASCIIOutStrings(self):
        # We just check that this call doesn't raise a UnicodeDecodeError
        # (or any other exception, for that matter).
        self.migration.migrateWeblog(self.weblog_non_ascii)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigration09_15))
    return suite
