"""
$Id:
"""
# Test weblog with LP >= 0.9

from Products.LinguaPlone.tests.utils import makeContent
from Products.LinguaPlone.tests.utils import makeTranslation

from Products.Quills.tests import QuillsLinguaPloneTestCase
import transaction

class TestWeblogTranslation(
            QuillsLinguaPloneTestCase.QuillsLinguaPloneTestCase):

    def _setup(self):
        QuillsLinguaPloneTestCase.QuillsLinguaPloneTestCase._setup(self)

    def afterSetUp(self):
        self.login()
        self.setRoles(["Manager"])
        self.addLanguage('de')
        self.setLanguage('en')
        self.weblog_en = makeContent(self.folder, 'Weblog', 'weblog')
        self.weblog_en.setLanguage('en')

    def testTranslationKeepSameIdInDifferentFolders(self):
        self.weblog_de = makeTranslation(self.weblog_en, 'de')
        englishpost = makeContent(self.weblog_en, 'WeblogEntry', 'post')
        englishpost.setLanguage('en')
        germanpost = makeTranslation(englishpost, 'de')
        self.assertEqual(englishpost.getId(), germanpost.getId())

    def testTranslationIsMovedToTranslatedFolder(self):
        self.weblog_de = makeTranslation(self.weblog_en, 'de')
        englishpost = makeContent(self.weblog_en, 'WeblogEntry', 'post')
        englishpost.setLanguage('en')
        germanpost = makeTranslation(englishpost, 'de')
        self.failUnless(englishpost in self.weblog_en.objectValues())
        self.failUnless(germanpost in self.weblog_de.objectValues())

    def testFolderTranslationMoveTranslatedContent(self):
        english1 = makeContent(self.weblog_en, 'WeblogEntry', 'entry1')
        english1.setLanguage('en')
        english2 = makeContent(self.weblog_en, 'WeblogEntry', 'entry2')
        english2.setLanguage('en')
        german1 = makeTranslation(english1, 'de')
        german2 = makeTranslation(english2, 'de')
        transaction.savepoint(optimistic=True)
        self.weblog_de = makeTranslation(self.weblog_en, 'de')
        self.failUnless(english1.getId() in self.weblog_en.objectIds())
        self.failUnless(english2.getId() in self.weblog_en.objectIds())
        self.failIf(english1.getId() in self.weblog_de.objectIds())
        self.failIf(english2.getId() in self.weblog_de.objectIds())
        self.failUnless(german1.getId() in self.weblog_de.objectIds())
        self.failUnless(german2.getId() in self.weblog_de.objectIds())
        self.failIf(german1.getId() in self.weblog_en.objectIds())
        self.failIf(german2.getId() in self.weblog_en.objectIds())

    def testSetLanguageMoveTranslatedContent(self):
        self.weblog_de = makeTranslation(self.weblog_en, 'de')
        en2de = makeContent(self.weblog_en, 'WeblogEntry', 'entry2')
        en2de.setLanguage('en')
        transaction.savepoint(optimistic=True)
        en2de.setLanguage('de')
        self.failIf(en2de.getId() in self.weblog_en.objectIds())
        self.failUnless(en2de.getId() in self.weblog_de.objectIds())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    from Products.LinguaPlone.tests import LinguaPloneTestCase
    LinguaPloneTestCase # PYFLAKES
    suite.addTest(makeSuite(TestWeblogTranslation))
    return suite
