#
# Authors: Brian Skahan <bskahan@etria.com>
#          Tom von Schwerdtner <tvon@etria.com>
#
# Copyright 2004-2005, Etria, LLP
#
# This file is part of Quills
#
# Quills is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Quills is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Quills; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##############################################################################
"""Migrate from 0.9 to 1.5.
"""

# CMF imports
from Products.CMFCore.utils import getToolByName

# Product imports
from Products.Quills import MetaWeblogAPI
from Products.Quills import config

# plonetrackback imports
from quills.trackback.interfaces import ITrackbackOutManager

# Standard lib imports
from StringIO import StringIO

# Zope imports
from Acquisition import aq_base


class Migration(object):
    """Migrate from 0.9 to 1.5
    """

    def __init__(self, site, out):
        self.site = site
        self.out = out
        self.catalog = getToolByName(self.site, 'portal_catalog')

    def migrate(self):
        """Run migration on site object passed to __init__.
        """
        print >> self.out, u"Migrating Quills 0.9 -> 1.5"
        self.removeEntryCategoriesIndex()
        self.removeBloggerAPIFromRPCAuth()
        # Updating of schemas is handled in the installer
        weblogs = self.catalog(meta_type='Weblog')
        for weblog in weblogs:
            self.migrateWeblog(weblog.getObject())

    def removeEntryCategoriesIndex(self):
        """Remove the getEntryCategories index if present.

        We now use the Subject index, so we can zap it.
        """
        index = 'getEntryCategories'
        if index in self.catalog.indexes():
            self.catalog.manage_delIndex(index)
            print >> self.out, u"Deleted getEntryCategories index"

    def removeBloggerAPIFromRPCAuth(self):
        # Define the auth methods that we need to remove from RPCAuth
        authMethods = [
            'blogger/getTemplate',
            'blogger/setTemplate',
            'blogger/deletePost',
            'blogger/editPost',
            'blogger/newPost',
            'blogger/getRecentPosts',
            'blogger/getUserInfo',
            'blogger/getUsersBlogs',
            ]
        rpcauth = self.site.RPCAuth
        # Remove the auth methods as they have persistent references to
        # code from the former BloggerAPI module. This doesn't give an
        # error if it has already been called.
        rpcauth.removeAuthProvider(authMethods)
        # Now add back the MetaWeblogAPI auth methods as there are some
        # blogger ones in there.
        rpcauth.addAuthProvider(MetaWeblogAPI.authMethods,
                                MetaWeblogAPI.genericMetaWeblogAuth)

    def migrateWeblog(self, weblog):
        """Migrate a weblog.
        """
        print >> self.out, \
            u'Migrating Weblog: %s' % "/".join(weblog.getPhysicalPath())
        self.removeBloggerAPI(weblog)
        self.migrateWeblogTopics(weblog)
        for brain in weblog.getAllEntries():
            entry = brain.getObject()
            self.migrateTrackbacksForEntry(entry)
            self.migrateCategoriesForEntry(entry)

    def removeBloggerAPI(self, weblog):
        """Make sure that BloggerAPI is gone from both the weblog instance
        and its associated RPCAuth instance.
        """
        try:
            delattr(weblog, 'blogger')
        except AttributeError:
            # It's already gone - almost certainly in the 08to09 migration,
            # but there's no harm in being sure ;-).
            pass
        # Now alias metaWeblog to blogger for Performancing compatibility.
        # See <http://performancing.com/node/3158> for more details.
        if not hasattr(weblog, 'metaWeblog'):
            weblog.metaWeblog = MetaWeblogAPI.MetaWeblogAPI()
        weblog.blogger = weblog.metaWeblog

    def migrateTrackbacksForEntry(self, entry):
        """Swap to multiple trackback URLs stored with an adapter.
        """
        if not hasattr(entry, 'trackbackURLs'):
            # The attribute doesn't exist anymore so nothing to
            # migrate!
            return
        # Adapt to the interface for storing trackback details
        tbim = ITrackbackOutManager(entry)
        # Get the existing URLs by attribute access as the methods are no longer
        # available - the schema no longer defines them.
        urls = getattr(entry, 'trackbackURLs', None)
        if urls:
            #print >> self.out, \
            #    u"Migrating trackbacks for %s." % "/".join(entry.getPhysicalPath())
            wftool = getToolByName(entry, 'portal_workflow')
            review_state = wftool.getInfoFor(entry, 'review_state')
            if review_state == 'published':
                # If the entry is published, the URLs will already have been pinged
                tbim.setPingedURLs(urls)
            else:
                # ... otherwise, they still need to be pinged.
                tbim.setURLsToPing(urls)
        # Remove the attribute.
        del entry.trackbackURLs

    def migrateCategoriesForEntry(self, entry):
        """Migrate the old categories to standard subjects.
        """
        # Make sure we don't acquire the attribute in the check
        if getattr(aq_base(entry), 'entryCategories', None) is None:
            # Nothing to do here.
            return
        # Get the existing categories by direct attribute access as
        # the methods are no longer available - the schema no longer
        # defines them.
        cats = list(aq_base(entry).entryCategories)
        # Get the existing subject keywords
        existingSubjects = list( entry.Subject() )
        # Add the two together
        subjects = existingSubjects[:] # Hard copy
        subjects.extend(cats)
        # Filter them to avoid duplicates, can happen with multiple
        # calls to the migration or because you already tagged the
        # entry with that keyword.
        uniqueSubjects = {}
        for subject in subjects:
            uniqueSubjects[subject] = 1
        subjects = uniqueSubjects.keys()
        # See if anything changed
        subjects.sort()
        existingSubjects.sort()
        if subjects != existingSubjects:
            # Set the new subjects list
            entry.setSubject(subjects)
            # Update the catalog
            self.catalog.reindexObject(entry)
            #print >> self.out, \
            #    "Migrated categories for '%s' to subjects: %r" % (
            #    "/".join(entry.getPhysicalPath()),
            #    subjects)
        # Remove the entryCategories attribute
        del entry.entryCategories

    def migrateWeblogTopics(self, weblog):
        """Migrate a weblog topic.
        """
        # XXX Need to disable WeblogTopic content type after migration of topics
        if getattr(weblog.aq_explicit, 'topic_images', None) is None:
            typestool = getToolByName(weblog, 'portal_types')
            typestool.constructContent('Folder', container=weblog,
                                       id=config.TOPIC_IMAGE_FOLDER_ID,
                                       title=u'Topic Images')
            print >> self.out, u"Created topic_images folder in weblog"
        topic_images = weblog.topic_images
        to_be_deleted = []
        for ob in weblog.objectValues():
            if getattr(ob, 'portal_type', None) == 'WeblogTopic':
                title = ob.Title()
                title = title.replace('/', '_').replace('?', '_')
                img = StringIO(ob.getTopicImage())
                if getattr(topic_images, title, None) is None:
                    # No title, so existing images folder as we
                    # otherwise just created the folder *with* a
                    # title.
                    plone_tool = getToolByName(self, 'plone_utils')
                    id_title = plone_tool.normalizeString(title, context=ob) 
                    topic_images.invokeFactory('Image', id=id_title) 
                    newimg = getattr(topic_images, id_title) 
                    newimg.setImage(img)
                    print >> self.out, u"Copied topic image."
                to_be_deleted.append(ob.getId())
        weblog.manage_delObjects(ids=to_be_deleted)
