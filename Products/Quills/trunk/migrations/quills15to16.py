"""Migrate from 1.5 to 1.6.
"""

# CMF imports
from Products.CMFCore.utils import getToolByName

class Migration(object):
    """Migrate from 1.5 to 1.6
    """

    def __init__(self, site, out):
        self.site = site
        self.out = out
        self.catalog = getToolByName(self.site, 'portal_catalog')

    def migrate(self):
        """Run migration on site object passed to __init__.
        """
        print >> self.out, u"Migrating Quills 1.5 -> 1.6"
        self.removeQuillsTool()
        weblogs = self.catalog(meta_type='Weblog')
        for weblog in weblogs:
            self.migrateWeblog(weblog.getObject())

    def removeQuillsTool(self):
        """Remove quills_tool from the portal.
        """
        if self.site.hasObject('quills_tool'):
            print >> self.out, u"Removing 'quills_tool'."
            self.site.manage_delObjects(ids=['quills_tool',])
        else:
            print >> self.out, u"'quills_tool' already removed."

    def migrateWeblog(self, weblog):
        """Migrate a weblog.
        """
        msg = u'Migrating Weblog: %s'
        print >> self.out, msg % '/'.join(weblog.getPhysicalPath())
        self.removeRemoteBloggingAttributes(weblog)
        self.migrateWeblogViewConfiguration(weblog)
        self.movePostsToWeblogRoot(weblog)

    def migrateWeblogViewConfiguration(self, weblog):
        # Use direct attribute access to get hold of previously defined AT
        # schema fields on weblog, and store them with the new
        # IWeblogViewConfiguration
        pass

    def fixUpWorkflows(self):
        pass

    def movePostsToWeblogRoot(self, weblog):
        weblogPath = '/'.join(weblog.getPhysicalPath())
        archives = self.catalog(path=weblogPath,
                               portal_type='WeblogArchive')
        entriesByPath = {}
        for archive in archives:
            entries = self.catalog(path={ 'query' : archive.getPath(),
                                          'depth' : 1 },
                                   portal_type='WeblogEntry')
            if entries:
                entriesByPath[archive.getObject()] = [ entry.getId for entry in entries ]

        for archive, entries in entriesByPath.items():
            cut = archive.manage_cutObjects(entries)
            weblog.manage_pasteObjects(cut)
        

    def removeWeblogAuthorRole(self):
        pass

    def removeRemoteBloggingAttributes(self, weblog):
        try:
            delattr(weblog, 'metaWeblog')
            msg = u"Removed 'metaWeblog' from %s."
        except AttributeError:
            msg = u"No 'metaWeblog' found on %s."
        print >> self.out, msg % '/'.join(weblog.getPhysicalPath())
        try:
            delattr(weblog, 'blogger')
            msg = u"Removed 'blogger' from %s."
        except AttributeError:
            msg = u"No 'blogger' found on %s."
        print >> self.out, msg % '/'.join(weblog.getPhysicalPath())
