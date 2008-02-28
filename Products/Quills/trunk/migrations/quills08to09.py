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
"""Migrate from 0.8 to 0.9."""

from Products.CMFCore.utils import getToolByName
from Products.Quills import MetaWeblogAPI


class Migration(object):
    u"""Migrate from 0.8 to 0.9."""

    def __init__(self, site, out):
        self.site = site
        self.out = out
        self.tool = getToolByName(site, 'quills_tool')
        self.workflow = getToolByName(site, 'portal_workflow')

    def migrate(self):
        u"""Run migration on site object passed to __init__."""
        print >> self.out, u"Migrating Quills 0.8 -> 0.9"

        self.catalog = getToolByName(self.site, 'portal_catalog')
        self.qtool = getToolByName(self.site, 'quills_tool')

        weblogs = self.catalog(meta_type='Weblog')
        print >> self.out, u"Migrating %s weblogs..." % len(weblogs)
        for weblog in weblogs:
            self.migrateWeblog(weblog.getObject())

    def migrateWeblog(self, weblog):
        u"""Migrate a weblog."""
        print >> self.out, u'Migrating Weblog: %s...' % "/".join(weblog.getPhysicalPath())

        delattr(weblog, 'metaWeblog')
        delattr(weblog, 'blogger')

        RPCAuth = self.qtool.findRPCAuth(weblog)

        weblog.metaWeblog = MetaWeblogAPI.MetaWeblogAPI().__of__(weblog)
        weblog.metaWeblog.setupRPCAuth(RPCAuth)

        weblog.trackbackEnabled = False

        if not hasattr(weblog.aq_inner.aq_explicit, 'archive'):
            self.site.portal_types.constructContent('WeblogArchive',
                    weblog, 'archive', title='Archive', archive_type='root')

        # Create a place to stick any WeblogEntry contents (they were folderish
        # in 0.8)
        if not hasattr(weblog.aq_inner.aq_explicit, 'attachments'):
            self.site.portal_types.constructContent('Folder',
                    weblog, 'attachments', title='Attachments')

        for id, item in weblog._tree.items():
            if item.meta_type == 'WeblogEntry':
                if item.Title():
                    self.migrateWeblogEntry(weblog, item, id)
            elif item.meta_type == 'WeblogTopic':
                self.migrateWeblogTopic(weblog, item, id)
            else:
                self.migrateOther(weblog, item, id)

        self.migrateDrafts(weblog)

        weblog.reindexObject()

    def moveAttachments(self, weblog, entry):
        u"""Move anything in the folderish WeblogEntry.

        Objects are moved to ${weblog}/attachments/${entry-id}/
        The entry body needs to be rewritten in case any of the attachments are
        directly referenced, this means doing something like:

        body.replace('${entry-id}/${attachment-id}',
                'attachments/${entry-id}/${attachment-id}')
        """
        id = entry.getId()

        # 1: Get a list of items in the Folderish entry
        # 2: Move items to attachments folder
        # 3: string.replace() the body to alter any references to attachments
        attachments = getattr(weblog.aq_inner.aq_explicit, 'attachments')

    def migrateWeblogEntry(self, weblog, entry, id):
        """Migrate a weblog entry.

        Take a stale entry from Weblog._tree (an OOBTree) and re-produce it
        as a current WeblogEntry in the archive.

        TODO:
        * Don't just check EffectiveDate, see if it is actually published.
        """

        #self.moveAttachments(weblog, entry)

        print >> self.out, u"Migrating entry: '%s'" % "/".join(entry.getPhysicalPath())

        archive = getattr(weblog.aq_inner.aq_explicit, 'archive')

        if entry.getEffectiveDate():
            dest = archive.createPath(entry.getEffectiveDate())
            self.site.portal_types.constructContent('WeblogEntry', dest, id,
                    title=entry.Title())

            obj = getattr(dest.aq_inner.aq_explicit, id)

            obj.setEffectiveDate(entry.getEffectiveDate())
            obj.setText(entry.__of__(obj).body)
            obj.setDescription(entry.__of__(obj).Description())
            obj.setEntryCategories(entry.getEntryCategories())
            obj.reindexObject()

            self.workflow.doActionFor(obj, 'publish_in_place',
                    'quills_workflow')

        else:
            self.site.portal_types.constructContent('WeblogEntry', weblog, id,
                    title=entry.Title())

    def migrateWeblogTopic(self, weblog, topic, id):
        """Copy WeblogTopic objects from _tree to the Weblog."""
        self.site.portal_types.constructContent('WeblogTopic', weblog, 
                id, title=topic.Title(), topicImage=topic.getTopicImage())

    def migrateOther(self, weblog, item, id):
        """Copy any additional objects from _tree to the new Weblog object."""
        pass

    def migrateDrafts(self, weblog):
        """Move all drafts out of the WeblogDrafts folderish object in
        preparation for it to disappear from the codebase in Quills 1.0.
        """
        filter = {'portal_type' : 'WeblogDrafts'}
        dfs = weblog.contentValues(filter=filter)
        wefilter = {'portal_type' : 'WeblogEntry'}
        for folder in dfs:
            ids = folder.contentIds(filter=filter)
            if ids:
                cp = folder.manage_cutObjects(ids)
                weblog.manage_pasteObjects(cp)
                for id in ids:
                    ob = getattr(weblog.aq_explicit, id)
                    ob.reindexObject()
        dfids = [ob.getId() for ob in dfs]
        weblog.manage_delObjects(dfids)
