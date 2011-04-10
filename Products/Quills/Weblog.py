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

# Zope imports
from zope.interface import implements
from zope.component import getUtility
from AccessControl import ClassSecurityInfo

# Archetypes imports
from Products.Archetypes.public import BaseFolderSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import TextField
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import BaseFolder
from Products.Archetypes.public import registerType

from Products.Archetypes.Marshall import PrimaryFieldMarshaller

# Plone imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
# BBB: ISelectableBrowserDefault needed for Plone3
# See:
#  * http://plone.org/products/quills/issues/121
#  * http://plone.org/products/quills/issues/6
# a workaround for https://dev.plone.org/plone/ticket/7226

# Quills imports
from Products.Quills import QuillsMessageFactory as _
from quills.core.interfaces import IWeblog, IWeblogEntry
from quills.app.interfaces import IWeblogEnhancedConfiguration
from quills.app.topic import TopicContainer
from quills.app.topic import AuthorContainer
from quills.app.archive import ArchiveContainer
from quills.app.archive import YearArchive
from quills.app.utilities import BloggifiedCatalogResults
from quills.app.weblog import WeblogMixin

# Local imports
import config
import permissions as perms

# This won't work because the `weblog' object is not aq-wrapped, so it's not
# possible to use invokeFactory.
#def weblogTopicImageFolderSetup(weblog, event):
#    has_topic_images = hasattr(aq_base(weblog), 'topic_images')
#    # Create folder to store topic images
#    if config.CREATE_TOPIC_IMAGES_FOLDERS and not has_topic_images:
#        weblog.invokeFactory('Folder', id='topic_images', title='Topic Images')


WeblogSchema = BaseFolderSchema.copy() + Schema((

    # This is sort of cheating.  We are stealing the Dublin Core 'description'
    # field for our purposes, but then I don't seen any reason to duplicate the
    # information.
    TextField('description',
              searchable=1,
              accessor='Description',
              widget=TextAreaWidget(
                     label=_(u'label_weblog_description', default=u'Description'),
                     description=_(u'help_weblog_description', default=u'A brief description of this weblog. This text will be displayed at the top of the page before any weblog entries.'),
                     ),
              ),
    ),
    marshall=PrimaryFieldMarshaller(),
    )

# The subject is not language-specific
WeblogSchema['subject'].languageIndependent = True


def createSpecialFolders(blog, event):
    """Create folders for uploads and topic images. Supposed to be triggered
    on Weblog creation.
    
    We use '_createObjectByType' here so that we don't have to allow the
    'Folder' content type for the weblog.
    """
    has_topic_images = hasattr(blog, 'topic_images')
    typestool = getToolByName(blog, 'portal_types')
    if config.CREATE_TOPIC_IMAGES_FOLDERS and not has_topic_images:
        typestool.constructContent('Folder', container=blog,
            id=config.TOPIC_IMAGE_FOLDER_ID,
            title=u'Topic Images')
    has_uploads = hasattr(blog, 'uploads')
    # Create folder to store topic images
    if config.CREATE_UPLOAD_FOLDERS and not has_uploads:
        typestool.constructContent('Folder',container=blog,
            id=config.UPLOAD_FOLDER_ID,
            title=u'Uploads')

class Weblog(WeblogMixin, BaseFolder, BrowserDefaultMixin):
    """Weblog object.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblog, Weblog)
    True
    
    >>> from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
    >>> verifyClass(ISelectableBrowserDefault, Weblog)
    True
    """

    implements(IWeblog)

    schema = WeblogSchema
    security = ClassSecurityInfo()

    _at_rename_after_creation = True

    security.declareProtected(perms.View, 'getTitle')
    def getTitle(self):
        """See IWeblog.
        """
        return self.Title()

    security.declareProtected(perms.View, 'getId')
    def getId(self):
        """See IWeblog.
        """
        return self.id
 
    security.declareProtected(perms.View, 'getTopics')
    def getTopics(self):
        """See IWeblog.
        """
        topic_container = TopicContainer('topics').__of__(self)
        return topic_container.getTopics()

    security.declareProtected(perms.View, 'getTopicById')
    def getTopicById(self, id):
        """See IWeblog.
        """
        topic_container = TopicContainer('topics').__of__(self)
        return topic_container.getTopicById(id)

    security.declareProtected(perms.View, 'getSubArchives')
    def getSubArchives(self):
        """See IWeblogArchive.
        """
        config = IWeblogEnhancedConfiguration(self)
        archive_id = config.archive_format
        arch_container = ArchiveContainer(archive_id).__of__(self)
        if archive_id:
            # If there is an extra archive URL segment needed, then we inject
            # the ArchiveContainer into the acquisition chain for the returned
            # sub-archives
            return arch_container.getSubArchives()
        # Otherwise, we'll just use the ArchiveContainer's _getEntryYears
        # implementation to figure out what YearArchive objects to return
        # directly in the context of this IWeblog.
        years = arch_container._getEntryYears()
        return [YearArchive(year).__of__(self) for year in years]

    security.declareProtected(perms.View, 'getEntry')
    def getEntry(self, id):
        """See IWeblog.
        """
        catalog = getToolByName(self, 'portal_catalog')
        path = '/'.join(self.getPhysicalPath())
        results = catalog(
                meta_type=['WeblogEntry',],
                path={'query':path, 'level': 0},
                getId=id,)
        if results:
            return BloggifiedCatalogResults.wrap(results[0])
        else:
            return None

    security.declareProtected(perms.View, 'hasEntry')
    def hasEntry(self, id):
        """See IWeblog.
        """
        return self.getEntry(id) and True or False

    security.declareProtected(perms.View, 'getEntries')
    def getEntries(self, maximum=None, offset=0):
        """See IWeblog.
        """
        catalog = getToolByName(self, 'portal_catalog')
        weblog_config = IWeblogEnhancedConfiguration(self)
        results = catalog(
            meta_type=['WeblogEntry',],
            path={ 'query' : '/'.join(self.getPhysicalPath()),
                   'level' : 0, },
            sort_on='effective',
            sort_order='reverse',
            review_state={ 'query'    : weblog_config.published_states,
                           'operator' : 'or'})
        return BloggifiedCatalogResults(self._filter(results, maximum, offset))

    security.declareProtected(perms.ViewDrafts, 'getAllEntries')
    def getAllEntries(self, maximum=None, offset=0):
        """See IWeblog.
        """
        catalog = getToolByName(self, 'portal_catalog')
        path = '/'.join(self.getPhysicalPath())
        results = catalog(
                meta_type=['WeblogEntry',],
                path={'query':path, 'level': 0},
                sort_on = 'effective',
                sort_order = 'reverse')
        return BloggifiedCatalogResults(self._filter(results, maximum, offset))

    security.declareProtected(perms.ViewDrafts, 'getDrafts')
    def getDrafts(self, maximum=None, offset=0):
        """See IWeblog.
        """
        catalog = getToolByName(self, 'portal_catalog')
        weblog_config = IWeblogEnhancedConfiguration(self)
        path = '/'.join(self.getPhysicalPath())
        results = catalog(
                meta_type=['WeblogEntry',],
                path={'query':path, 'level': 0},
                sort_on = 'effective',
                sort_order = 'reverse',
                review_state = weblog_config.draft_states)
        return BloggifiedCatalogResults(self._filter(results, maximum, offset))

    security.declareProtected(perms.View, 'getAuthors')
    def getAuthors(self):
        """See IWeblog.
        """
        author_container = AuthorContainer('authors').__of__(self)
        return author_container.getAuthors()

    security.declareProtected(perms.View, 'getAuthorById')
    def getAuthorById(self, id):
        """See IWeblog.
        """
        author_container = AuthorContainer('authors').__of__(self)
        return author_container.getAuthorById(id)

    security.declareProtected(perms.AddContent, 'addEntry')
    def addEntry(self, title, excerpt, text, topics=[], id=None, pubdate=None,
                 mimetype=None):
        """See IWeblog.
        """
        if id is None:
            id = getUtility(IIDNormalizer).normalize(title)
        self.invokeFactory(id=id, type_name='WeblogEntry')
        entry = getattr(self, id)
        entry.setTitle(title)
        # if no mimetype was specified, we use the default
        if mimetype is None:
            mimetype = entry.getMimeType()
        entry.setText(text, mimetype=mimetype)
        entry.setExcerpt(excerpt)
        if topics:
            entry.setTopics(topics)
        if pubdate is not None:
            entry.setPublicationDate(pubdate)
        entry.reindexObject()
        return entry

    security.declareProtected(perms.AddContent, 'addFile')
    def addFile(self, content, mimetype, id=None, title=''):
        """See IWeblog.
        """
        if self.hasObject(config.UPLOAD_FOLDER_ID):
            upload_folder = getattr(self, config.UPLOAD_FOLDER_ID)
        else:
            upload_folder = self
        id = self._genUniqueId(folder=upload_folder, id=id, title=title)
        portal_type = self._getPortalTypeForMimeType(mimetype)
        upload_folder.invokeFactory(id=id,
                                    type_name=portal_type,
                                    title=title,
                                    file=content)
        return getattr(upload_folder, id)

    security.declareProtected(perms.DeleteContent, 'deleteEntry')
    def deleteEntry(self, entry_id):
        """See IWeblog.
        """
        self.manage_delObjects(ids=[entry_id,])

    security.declareProtected(perms.View, 'getWeblogContentObject')
    def getWeblogContentObject(self):
        """See IWeblog.
        """
        return self

    security.declareProtected(perms.View, 'getWeblog')
    def getWeblog(self):
        """See IWeblog.
        """
        return self
     

registerType(Weblog, config.PROJECTNAME)
