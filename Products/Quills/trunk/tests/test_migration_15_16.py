"""
$Id: test_migration_09_15.py 29081 2006-08-21 15:26:15Z tim2p $
"""

from Products.CMFCore.utils import getToolByName
from Products.Quills.migrations import quills15to16
from base import QuillsTestCase
from StringIO import StringIO

from Products.GenericSetup import EXTENSION, profile_registry
from Products.CMFPlone.interfaces import IPloneSiteRoot

profile_registry.registerProfile(
                    'testing',
                    'Quills',
                    'Extension profile for Quills migration tests',
                    'tests/profile',
                    'Quills',
                    EXTENSION,
                    for_=IPloneSiteRoot)


class TestMigration15_16(QuillsTestCase):

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
        self.migration = quills15to16.Migration(site=self.portal,
                                                out=self.out)
        # Add an object with the name 'quills_tool'
        self.portal.invokeFactory('Folder', id='quills_tool')
        # Add metaWeblog and blogger (dummy) attributes
        self.weblog.metaWeblog = 'foo'
        self.weblog.blogger = 'bar'
        # transaction to allow copy/move 
        from transaction import savepoint; savepoint()

    def test_migrateWeblog(self):
         pass

    def test_migrateWeblogEntry(self):
        weblog = self.weblog
        # add a WeblogArchive type
        setup_tool = getToolByName(weblog, 'portal_setup')
        setup_tool.runImportStepFromProfile('profile-Quills:testing','typeinfo')

        weblog.invokeFactory('WeblogArchive', id='archive')
        archive = weblog.archive
        archive.invokeFactory('WeblogArchive', id='2007')
        for subId in ['1','2']:
            archive['2007'].invokeFactory('WeblogArchive', id=subId)
            subArchive = archive['2007'][subId]

        entriesPaths = [ archive['2007']['1'],archive['2007']['2'],archive['2007']['1'],archive['2007']['2'],archive['2007']['1'],archive['2007']['2']]
        answer = []
        for i in range(5):
            entryId = 'entry%s' % i
            entriesPaths[i].invokeFactory('WeblogEntry', id=entryId)
            answer.append(entryId)

        from transaction import savepoint; savepoint()
        self.migration.movePostsToWeblogRoot(weblog)
        entries = [ entryId for entryId in weblog.contentIds()
                            if entryId.startswith('entry') ]
        entries.sort()
        self.failUnless(answer == entries)
        
    def test_removeQuillsTool(self):
        qt = getToolByName(self.portal, 'quills_tool', None)
        self.failIf(qt is None)
        del qt
        # Migrate and check the results.
        self.migration.removeQuillsTool()
        qt = getToolByName(self.portal, 'quills_tool', None)
        self.failUnless(qt is None)

    def test_removeRemoteBloggingAttributes(self):
        weblog = self.weblog
        has_metaweblog = getattr(weblog.aq_base, 'metaWeblog', False)
        has_blogger = getattr(weblog.aq_base, 'blogger', False)
        self.failUnless(has_metaweblog and has_blogger)
        self.migration.removeRemoteBloggingAttributes(weblog)
        has_metaweblog = getattr(weblog.aq_base, 'metaWeblog', False)
        has_blogger = getattr(weblog.aq_base, 'blogger', False)
        self.failIf(has_metaweblog)
        self.failIf(has_blogger)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigration15_16))
    return suite
