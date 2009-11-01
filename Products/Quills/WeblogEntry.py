#
# Authors: Brian Skahan <bskahan@etria.com>
#          Tom von Schwerdtner <tvon@etria.com>
#
# Copyright 2004-2005, Etria, LLP
# # This file is part of Quills
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
###############################################################################

# Zope imports
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from DateTime.DateTime import DateTime

# Plone imports
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import log
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

# Archetypes imports
from Products.Archetypes.public import BaseSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import TextField
from Products.Archetypes.public import TextAreaWidget
from Products.Archetypes.public import RichWidget
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType
from Products.Archetypes.Marshall import RFC822Marshaller

# Quills imports
from Products.Quills import QuillsMessageFactory as _
from quills.core.interfaces import IWorkflowedWeblogEntry
from quills.app.topic import Topic
from quills.app.topic import AuthorTopic
from quills.app.utilities import QuillsMixin
from quills.app.interfaces import IWeblogEnhancedConfiguration

# Local imports
from config import PROJECTNAME
import permissions as perms

WeblogEntrySchema = BaseSchema.copy() + Schema((

    TextField('description',
              searchable=1,
              accessor='Description',
              widget=TextAreaWidget(
                     label=_(u'label_weblogentry_description', default=u'Excerpt'),
                     description=_(u'help_weblogentry_description', default='A brief introduction for this entry.'),
                     ),
              ),

    TextField('text',
              searchable=1,
              default_output_type='text/x-html-safe',
              widget=RichWidget(
                     label=_(u'label_text', default=u'Entry Text'),
                     rows=30,
                     ),
              ),
    ),
    marshall=RFC822Marshaller(),
)

# Move the subject/topic picking to the main edit view as it should be used
# for every edit, really.
WeblogEntrySchema['subject'].schemata = 'default'
# The subject is not language-specific
WeblogEntrySchema['subject'].languageIndependent = True,
# Make sure it is presented after the main text entry field.
WeblogEntrySchema.moveField('subject', after='text')
# Make sure the allowDiscussion field's default is None
WeblogEntrySchema['allowDiscussion'].default = None
# Put the discussion setting on the main page...
WeblogEntrySchema['allowDiscussion'].schemata = 'default'
# ... at the bottom, after the subject keywords.
WeblogEntrySchema.moveField('allowDiscussion', after='subject')


class WeblogEntry(QuillsMixin, BaseContent, BrowserDefaultMixin):
    """Basic Weblog Entry.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWorkflowedWeblogEntry, WeblogEntry)
    True
    """

    implements(IWorkflowedWeblogEntry)

    schema = WeblogEntrySchema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    security.declareProtected(perms.View, 'getTitle')
    def getTitle(self):
        """See IWeblogEntry.
        """
        return self.Title()

    security.declareProtected(perms.View, 'getTopics')
    def getTopics(self):
        """See IWeblogEntry.
        """
        weblog = self.getWeblog()
        keywords = self.Subject()
        return [Topic(kw).__of__(weblog) for kw in keywords]

    security.declareProtected(perms.View, 'getAuthors')
    def getAuthors(self):
        """See IWeblogEntry.
        """
        weblog = self.getWeblog()
        creators = self.Creators()
        return [AuthorTopic(creator).__of__(weblog) for creator in creators]

    security.declareProtected(perms.View, 'getExcerpt')
    def getExcerpt(self):
        """See IWeblogEntry.
        """
        # This is just an alias for Description in this case.
        return self.Description()

    security.declareProtected(perms.EditContent, 'setExcerpt')
    def setExcerpt(self, excerpt):
        """See IWeblogEntry.
        """
        self.setDescription(excerpt)

    security.declareProtected(perms.EditContent, 'setTopics')
    def setTopics(self, topic_ids):
        """See IWeblogEntry.
        """
        self.setSubject(topic_ids)

    def setText(self, text, mimetype=None):
        """docstring for setText"""
        # if no mimetype was specified, we use the default
        if mimetype is None:
            mimetype = self.getMimeType()
        
        if hasattr(self, 'text'):
        	self.text.update(text, self, mimetype=mimetype)
       	else:
        	field = self.getField('text')
        	field.set(self, text, mimetype=mimetype)

    security.declareProtected(perms.EditContent, 'edit')
    def edit(self, title, excerpt, text, topics, mimetype=None):
        """See IWeblogEntry.
        """
        # if no mimetype was specified, we use the default
        if mimetype is None:
            mimetype = self.getMimeType()
        self.setText(text, mimetype=mimetype)
        self.setTitle(title)
        self.setExcerpt(excerpt)
        if topics:
            self.setTopics(topics)
        else:
            self.setTopics([])
        self.reindexObject()

    security.declareProtected(perms.View, 'effective')
    def effective(self):
        """Answer the date this entry became visible (published), or the
           creation date if the former is not defined.

           This is essentially a hotfix because Quills expects the effective
           date always to be defined, which is not the case (see Quills
           issue #126). 
           
           This is what fatsyndication feedentry does also. But here we are
           not redefining getEffectiveDate because "effective" will be used
           for cataloging.
        """
        return self.getField('effectiveDate').get(self) or self.created()

    security.declareProtected(perms.View, 'getPublicationDate')
    def getPublicationDate(self):
        """See IWeblogEntry.
        """
        return self.getEffectiveDate()

    security.declareProtected(perms.View, 'getMimeType')
    def getMimeType(self):
        """See IWeblogEntry.
        """
        # (ATCT handles the mechanics for determining the default for us)
        return self.text.getContentType()

    security.declareProtected(perms.EditContent, 'setPublicationDate')
    def setPublicationDate(self, datetime):
        """See IWeblogEntry.
        """
        self.setEffectiveDate(datetime)

    security.declareProtected(perms.EditContent, 'publish')
    def publish(self, pubdate=None):
        """See IWorkflowedWeblogEntry.
        """
        if self.isPublished():
            # do nothing if the entry has already been published
            return
        # XXX Need to be able to handle std library datetime objects for pubdate
        if pubdate is None:
            pubdate = DateTime()
        self.setPublicationDate(pubdate)
        wf_tool = getToolByName(self, 'portal_workflow')
        try:
            wf_tool.doActionFor(self, 'publish')
        except WorkflowException:
            state = wf_tool.getInfoFor(self, 'review_state')
            workflow = wf_tool.getWorkflowsFor(self)[0].id
            objectPath = "/".join(self.getPhysicalPath())
            log("WeblogEntry.publish failed, most probable because the current " 
                "state '%s' of workflow '%s' of entry '%s' does not define a "
                "transition 'publish'. To solve this either use another workflow, "
                "adapt the workflow, or restrain from using this method for now. "
                "Sorry." % (state, workflow, objectPath))
            raise
        self.reindexObject()

    security.declareProtected(perms.EditContent, 'retract')
    def retract(self):
        """See IWorkflowedWeblogEntry.
        """
        if not self.isPublished():
            # do nothing if the entry has already been private
            return
        wf_tool = getToolByName(self, 'portal_workflow')
        try:
            wf_tool.doActionFor(self, 'retract')
        except WorkflowException:
            state = wf_tool.getInfoFor(self, 'review_state')
            workflow = wf_tool.getWorkflowsFor(self)[0].id
            objectPath = "/".join(self.getPhysicalPath())
            log("WeblogEntry.retract failed, most probable because the current " 
                "state '%s' of workflow '%s' of entry '%s' does not define a "
                "transition 'retract'. To solve this either use another workflow, "
                "adapt the workflow, or restrain from using this method for now. "
                "Sorry." % (state, workflow, objectPath))
            raise
        self.setPublicationDate(None)
        self.reindexObject()

    security.declareProtected(perms.EditContent, 'isPublished')
    def isPublished(self):
        """See IWorkflowedWeblogEntry.
        """
        wf_tool = getToolByName(self, 'portal_workflow')
        review_state = wf_tool.getInfoFor(self, 'review_state')
        weblog_config = IWeblogEnhancedConfiguration(self.getWeblog())
        return review_state in weblog_config.published_states

    security.declareProtected(perms.View, 'getWeblogEntryContentObject')
    def getWeblogEntryContentObject(self):
        """See IWeblogEntry.
        """
        return self


registerType(WeblogEntry, PROJECTNAME)
