#
# Authors: Tom von Schwerdtner <tvon@etria.com>
#          Brian Skahan <bskahan@etria.com>
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

# Standard library imports
from OFS.SimpleItem import SimpleItem
import re

# Zope imports
from AccessControl import ClassSecurityInfo
import DateTime

# CMF imports
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions as CMFCorePermissions


authMethods = [
    'metaWeblog/getPost',
    'metaWeblog/deletePost',
    'metaWeblog/editPost',
    'metaWeblog/newPost',
    'metaWeblog/getRecentPosts',
    'metaWeblog/getUsersBlogs',
    'metaWeblog/getCategories'
    # We include Blogger API auth methods too as some implementations of
    # MetaWeblog API expect Blogger API to be present as well (i.e.
    # Performancing as of version 1.3).
    'blogger/getTemplate',
    'blogger/setTemplate',
    'blogger/deletePost',
    'blogger/editPost',
    'blogger/newPost',
    'blogger/getRecentPosts'
    ]

def genericMetaWeblogAuth(args):
    return args[1], args[2], args


class MetaWeblogAPI(SimpleItem):
    """http://www.xmlrpc.com/metaWeblogApi"""

    security = ClassSecurityInfo()
    excerptExtractor = re.compile("<h2 class=[\"|']QuillsExcerpt[\"|']>(.*)</h2>")
    divExtractor = re.compile("<div>((.*\n)*.*)</div>")

    def _getEffectiveDate(self, struct):
        """Extract the effective date from the struct, or return a default
        value.
        """
        ed = struct.get('pubDate',
                        struct.get('pubdate',
                                    None)
                        )
        if ed is None:
            ed = struct.get('dateCreated',
                            struct.get('datecreated',
                                       DateTime.DateTime())
                            )
        return ed

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'newPost')
    def newPost(self, blogid, username, password, struct, publish):
        """Create a new entry - either in draft folder or directly in archive."""
        self.plone_log('metaWeblog/newPost')

        weblog = self._getByUID(blogid)
        archive = getattr(weblog, 'archive')
        # We just store draft weblogentries in the weblog instance now.
        drafts = weblog

        # preparing the ingredients:
        body  = struct.get('description', struct.get('Description'))
        # if the body contains an excerpt, we extract it:
        excerpt, body = self.extractDescriptionFromBody(body)
        title = struct.get('title', struct.get('Title'))
        categories = struct.get('categories', struct.get('Categories'))
        effective_date = self._getEffectiveDate(struct)
        plone_tool = getToolByName(self, 'plone_utils')
        id = plone_tool.normalizeString(title)

        # let's get cooking:

        # 2005-12-13 tomster:
        # FIXME: nasty hack due to bug in workflow script: if we publish. we create
        # the new entry directly inside the archive (instead of in the drafts folder), if not,
        # we create it inside the drafts folder - this is done to avoid calling the 'publish'
        # transition which attempts to move the entry from the drafts folder into the archive
        # (which fails with a CopyError) but rather the 'publish_in_place'.
        if publish:
            try:
                dest = archive.createPath(effective_date)
            except Exception, e:
                self.plone_log("Cannot create destination: %s" % e)
                return False
        else:
            dest = drafts

        try:
            dest.invokeFactory(id=id, type_name='WeblogEntry', title=title)
        except Exception, e:
            self.plone_log("Cannot create WeblogEntry: %s" % e)
            return False

        entry = getattr(dest, id)
        entry.setText(body, mimetype='text/html')
        entry.setDescription(excerpt)
        if categories:
            entry.setSubject(categories)
        entry_uid = entry.UID()

        if publish:
            wf_tool = getToolByName(self, 'portal_workflow')
            # XXX [tim2p] I think this next call should be made whether the
            # item is to be published or not, but the whole dates/archives
            # thing is messy enough that I don't want to mess with it at
            # this stage.
            entry.setPublicationDate(effective_date)
            wf_tool.doActionFor(entry, 'publish_in_place', 'quills_workflow')
        entry.reindexObject()
        #self.plone_log("returning " + entry_uid)
        return entry_uid

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'editPost')
    def editPost(self, postid, username, password, struct, publish):
        """Implement MetaWeblog editPost"""

        self.plone_log('metaWeblog/editPost')

        entry = self._getByUID(postid)

        body  = struct.get('description', struct.get('Description'))
        excerpt, body = self.extractDescriptionFromBody(body)
        title = struct.get('title', struct.get('Title'))
        categories = struct.get('categories', struct.get('Categories'))
        # XXX We don't implement editing of the 'effective date' here
        # because that could lead to the date and the position in the
        # archive becoming out of sync.  Once we shift to traversal-not-
        # containment for the archives, this should probably be added.
        #effective_date = self._getEffectiveDate(struct)
        #entry.setEffectiveDate(effective_date)

        entry.setText(body, mimetype='text/html')
        entry.setTitle(title)
        entry.setDescription(excerpt)
        if categories:
            entry.setSubject(categories)
        else:
            entry.setSubject([])
        entry.reindexObject()

        # 2005-12-13 tomster:
        # for editing posts to work, we currently must avoid calling the publish workflow.

        #if publish:
        #   wf_tool = getToolByName(self, 'portal_workflow')
        #   entry.setEffectiveDate(DateTime.DateTime())
        #   wf_tool.doActionFor(entry, 'publish', 'quills_workflow')

        return True

    security.declareProtected(CMFCorePermissions.View, 'getPost')
    def getPost(self, postid, username, password):
        "Return a post as struct"

        self.plone_log('metaWeblog/getPost')

        obj = self._getByUID(postid)

        return self.entryStruct(obj)

    security.declareProtected(CMFCorePermissions.View, 'getCategories')
    def getCategories(self, blogid, username, password):
        """Returns a struct containing description, htmlUrl and rssUrl"""
        self.plone_log('metaWeblog/getCategories')
        weblog = self._getByUID(blogid)
        topics = weblog.getTopics()
        # 2005-12-13 tomster:
        # this is kind of ugly: according to the RFC we should return an array
        # of structs, but according to http://typo.leetsoft.com/trac/ticket/256
        # (at least) MarsEdit and ecto expect an array of strings containing the
        # category id.
        # Nigel: To accomidate ecto and other blogging clients we are going to
        # do this test to decide what format the topics should be returned in
        useragent = self.REQUEST['HTTP_USER_AGENT']
        if "ecto" in useragent or "Mars" in useragent:
            self.plone_log("MetaWeblogAPI", "Using ecto/MarsEdit hack")
            categories = [topic.getId() for topic in topics]
        else:
            categories = []
            for topic in topics:
                 categories.append(
                     {'description' : topic.getId(),
                      'htmlUrl' : topic.absolute_url(),
                      'rssUrl' : '%s/rss.xml' % topic.absolute_url(),
                     })
        return categories

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'deletePost')
    def deletePost(self, postid, username, password, publish):
        "Returns true on success, fault on failure"
        self.plone_log('metaWeblog/deletePost')

        entry = self._getByUID(postid)

        entry.aq_inner.aq_parent.manage_delObjects(entry.getId())

        return True

    security.declareProtected(CMFCorePermissions.View, 'getRecentPosts')
    def getRecentPosts(self, blogid, username, password, num):
        """Return 'num' recent posts to specified blog,

        returns a struct: The three basic elements are title, link and
        description. For blogging tools that don't support titles and links,
        the description element holds what the Blogger API refers to as
        'content'.
        """
        self.plone_log('metaWeblog/getRecentPosts for blogid %s' % blogid)

        weblog = self._getByUID(blogid)
        catalog = getToolByName(self, 'portal_catalog')
        results = catalog(
            meta_type='WeblogEntry',
            path='/'.join(weblog.getPhysicalPath()),
            sort_on='effective',
            sort_order='reverse')

        posts = []
        for item in results[:num]:
            obj = item.getObject()
            posts.append(self.entryStruct(obj))
        return posts

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'getUsersBlogs')
    def getUsersBlogs(self, appkey, username, password):
        """TODO: getUsersBlogs"""
        self.plone_log('metaWeblog/getUsersBlogs')
        #catalog = getToolByName(self, 'portal_catalog')
        #results = catalog(meta_type='Weblog', Creator=username)
        #blogs = []
        #for item in results:
        #    o = item.getObject()
        #    blogs.append(
        #            {'url': o.absolute_url(),
        #             'blogid' : o.UID(),
        #             'blogName' : o.title_or_id()}
        #            )
        # This method returns a list with details for *only* the weblog
        # instance that it is being called through.  The previous
        # implementation (commented out above) searched for all weblogs
        # across the portal and returned them.  However, this causes
        # problems with multi-user blogs - there can only be one 'creator' -
        # and doesn't make a lot of sense, to my mind.  If/when we
        # componentise this code into a Five-ish view, it should be
        # possible to implement a getUsersBlogs for the portal root object
        # that *does* return all weblogs within the portal.  Until that day
        # users will simply need to know the URL of the weblogs that they
        # wish to work with and set their remote blogging client
        # appropriately.
        parent_blog = self.aq_parent
        blogs = []
        blogs.append(
            {'url': parent_blog.absolute_url(),
             'blogid' : parent_blog.UID(),
             'blogName' : parent_blog.title_or_id(),
            }
        )
        return blogs

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'getUserInfo')
    def getUserInfo(self, appkey, username, password):
        """Returns returns a struct containing userinfo

        userid, firstname, lastname, nickname, email, and url.
        """

        self.plone_log('metaWeblog/getUserInfo')

        membership=getToolByName(self, 'portal_membership')
        info={'name':'no name','email':'no email','userid':'no user id'
               ,'firstname':'no first name','lastname':'no last name'
               ,'url':'no url'}
        member = membership.getAuthenticatedMember()
        if member:
            for key,value in info.items():
                info[key] = getattr(member,key,None) or value
        return info

    security.declarePrivate('entryStruct')
    def entryStruct(self, obj):
        """ returns the entry as a struct. Called by getRecentPosts and getPost."""

        # description is used here as container for the full entry, including the excerpt.
        # the excerpt is inserted as <h2> element. The whole description is wrapped in a <div>
        # to ensure validity of the resulting HTML and feeds.
        text = obj.getText()
        needToWrap = not text.startswith("<div>")
        if needToWrap:
            body = "<div>\n"
        else:
            body = ""
        if obj.getExcerpt() is not None and obj.getExcerpt() != "":
            excerpt = "<h2 class='QuillsExcerpt'>%s</h2>" % obj.getExcerpt()
            if needToWrap:
                body += excerpt + text
            else:
                # if there already exists a wrapping div, we need to inject the excerpt
                # inside of that, rather than just prepending it to the body.
                body += "<div>%s%s</div>" % (excerpt, self.divExtractor.split(text)[1])
        else:
            body += text
        if needToWrap:
            body += "\n</div>"

        struct = {
            'postid': obj.UID(),
            'dateCreated': obj.getPublicationDate().rfc822(),
            'title': obj.Title(),
            'description' : body,
            'categories' : [cat.getId() for cat in obj.getCategories()],
            'link' : obj.absolute_url()
        }

        return struct

    security.declarePrivate('extractDescriptionFromBody')
    def extractDescriptionFromBody(self, body):
        """ if the body contains a leading <h2> element, this is extraced as its description.
            the body without that element is then returned as new body.
        """
        excerpt = self.excerptExtractor.search(body)
        if excerpt == None:
            return "", body
        # use the regex to get the h2-element string
        excerptString = excerpt.groups()[0]
        # assuming, that there is only one excerpt element (which is why we're using
        # 'id' rather than 'class') we can now return the a leading, opening <div> plus
        # the second element of the split as body: re
        strippedBody = self.excerptExtractor.split(body)[0] + self.excerptExtractor.split(body)[2]
        return excerptString, strippedBody

    def _getByUID(self, uid):
        if uid=='0' or uid=='' or uid is None:
            return self
        qtool = getToolByName(self, 'quills_tool')
        return qtool.getByUID(uid)
