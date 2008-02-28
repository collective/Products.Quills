# Standard library imports
from StringIO import StringIO

# Zope imports
from transaction import commit
from zope.component import getUtility

# Plone imports
from Products.CMFCore.utils import getToolByName
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.storage import PortletAssignmentMapping

# Quills imports
from quills.app.portlets import tagcloud, weblogadmin, authors, recententries, quillslinks, \
    recentcomments, archive

# Local imports
import config
import migrations


def importFinalSteps(context):
    """Install Quills."""
    # Only run step if a flag file is present
    # see http://maurits.vanrees.org/weblog/archive/2007/06/discovering-genericsetup
    if context.readDataFile('quills_product_various.txt') is None:
        return
    out = StringIO()
    # install dependencies
    portal = context.getSite()
    quickinstaller = portal.portal_quickinstaller

    for dependency in config.DEPENDENCIES:
        print >> out, u"Installing dependency %s:" % dependency
        quickinstaller.installProduct(dependency)
        commit()

    setup_gs_profiles(portal, out)
    automigrate(portal, out)
    updateSchemas(portal, out) 
    weblogPortletSetup(portal, out)
    print >> out, u"Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()


def setup_gs_profiles(portal, out):
    setup_tool = getToolByName(portal, 'portal_setup')
    for extension_id in config.GS_DEPENDENCIES:
        try:
            setup_tool.runAllImportStepsFromProfile('profile-%s' % extension_id)
        except Exception, e:
            print >> out, "Error while trying to GS import %s (%s, %s)" \
                          % (extension_id, repr(e), str(e))
            raise


def automigrate(self, out):
    """Call the migration in so far it can be done safely.

    The 0.9 to 1.5 migration only removes old stuff we don't need
    anymore (which is always safe, as we check for the presence of it
    before removing it) and it migrates some old attributes when
    found. That's all safe (and unittested). :-)
    """
    migration1516 = migrations.quills15to16.Migration(site=self, out=out)
    migration1516.migrate()


def updateSchemas(self, out):
    """Update the schemas.
    """
    at = getToolByName(self, 'archetype_tool')
    class dummy:
        form = {}
    dummyRequest = dummy()
    contentTypes = ['Weblog',
                    'WeblogEntry',]
    for contentType in contentTypes:
        name = 'Quills.%s' % contentType
        print >> out, u"Migrating schema for %s." % name
        dummyRequest.form[name] = 1
    at.manage_updateSchema(update_all=1, REQUEST=dummyRequest)


DEFAULT_LEFT_PORTLETS = (
    ('tagcloud', tagcloud.Assignment, {}),
    ('archive', archive.Assignment, {}),
    ('quillslinks', quillslinks.Assignment, {}),
    )
DEFAULT_RIGHT_PORTLETS = (
    ('weblogadmin', weblogadmin.Assignment, {}),
    ('recententries', recententries.Assignment, {}),
    ('recentcomments', recentcomments.Assignment, {}),
    ('authors', authors.Assignment, {}),
    )

def weblogPortletSetup(portal, out):
    left_column = getUtility(IPortletManager, name="plone.leftcolumn")
    left_category = left_column[CONTENT_TYPE_CATEGORY]
    right_column = getUtility(IPortletManager, name="plone.rightcolumn")
    right_category = right_column[CONTENT_TYPE_CATEGORY]
    left_portlets = left_category.get('Weblog', None)
    right_portlets = right_category.get('Weblog', None)
    # It may be that it hasn't been created yet, so just to be safe:
    if left_portlets is None:
        left_category['Weblog'] = PortletAssignmentMapping()
        left_portlets = left_category['Weblog']
    if right_portlets is None:
        right_category['Weblog'] = PortletAssignmentMapping()
        right_portlets = right_category['Weblog']
    for name, assignment, kwargs in DEFAULT_LEFT_PORTLETS:
        if not left_portlets.has_key(name):
            left_portlets[name] = assignment(**kwargs)
    for name, assignment, kwargs in DEFAULT_RIGHT_PORTLETS:
        if not right_portlets.has_key(name):
            right_portlets[name] = assignment(**kwargs)
