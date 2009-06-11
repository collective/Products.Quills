"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.
Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase
from Products.Five.testbrowser import Browser as BaseBrowser

# Let Zope know about the products we need. Only "old style" products with
# the "Products" prefix need to appear here. 
ZopeTestCase.installProduct('fatsyndication')
ZopeTestCase.installProduct('Quills')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# Set up a Plone site, and apply the Quills extension profile
setupPloneSite(products=['Quills'])


class Browser(BaseBrowser):

    def addAuthorizationHeader(self, user=PloneTestCase.default_user,
                               password=PloneTestCase.default_password):
        """Add an authorization header using the given or default credentials.
        """
        self.addHeader('Authorization', 'Basic %s:%s' % (user, password))
        return self


class QuillsTestCaseMixin:
    """Base class for integration tests for the 'Quills' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """
    def getBrowser(self, logged_in=False):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if logged_in:
            browser.addAuthorizationHeader()
        return browser

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.weblog = self.createBlog('weblog')
        self.portal.portal_workflow.doActionFor(self.portal.weblog, "publish")

    def createBlog(self, id):
        """Create a Weblog."""
        self.portal.invokeFactory('Weblog', title="Test Weblog", id=id)
        return self.portal[id]
    
class QuillsTestCase(QuillsTestCaseMixin, PloneTestCase.PloneTestCase):
    """Base class for integration tests for the 'Quills' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """


class QuillsFunctionalTestCase(QuillsTestCaseMixin, PloneTestCase.FunctionalTestCase):
    """ a class for running functional tests."""


class QuillsDocTestCase(QuillsTestCaseMixin, PloneTestCase.PloneTestCase):
    """Base class for integration tests for the 'Quills' product. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """


class QuillsContributorDocTestCase(QuillsDocTestCase):
    """As QuillsDocTestCase, but only gives the logged-in user the 'Contributor'
    role.
    """

    def afterSetUp(self):
        self.setRoles(('Contributor', 'Reviewer'))
        self.portal.invokeFactory('Weblog', id='weblog')
        self.weblog = self.portal.weblog
