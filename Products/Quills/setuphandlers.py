# Standard library imports
from StringIO import StringIO

# Zope imports
from transaction import commit

# Plone imports
from Products.CMFCore.utils import getToolByName

# Quills imports
from quills.app.setuphandlers import addNewDiscussionReplyFormAction
from quills.app.setuphandlers import delNewDiscussionReplyFormAction

# Local imports
import config
import migrations


def installFinalSteps(context):
    """Install Quills.
    """
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
    
    automigrate(portal, out)
    updateSchemas(portal, out)
    addNewDiscussionReplyFormAction(portal, out)
    print >> out, u"Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()

def uninstallFinalSteps(context):
    """Uninstall Quills stuff that GS profiles cannot catch.
    """
    if context.readDataFile('quills_product_various.txt') is None:
        return
    out = StringIO()
    portal = context.getSite()
    delNewDiscussionReplyFormAction(portal, out)
    return out.getvalue()

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


def updateDefaultPageTypes(portal, out):
    """Allow a Weblog to be used on the front page of the site.
    """
    ptool = getToolByName(portal, 'portal_properties')
    default_page_types = ptool.site_properties.getProperty('default_page_types')
    # make it mutable
    default_page_types = list(default_page_types)
    if 'Weblog' not in default_page_types:
        default_page_types.append('Weblog')
        ptool.site_properties._updateProperty('default_page_types',
                                              default_page_types)
        msg = u"'Weblog' added to the list of default_page_types."
    else:
        msg = u"'Weblog' already in the list of default_page_types."
    print >> out, msg
