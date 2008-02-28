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
###############################################################################

from Products.Archetypes.public import BaseSchema
from Products.Archetypes.public import Schema
from Products.Archetypes.public import ImageField
from Products.Archetypes.public import ImageWidget
from Products.Archetypes.public import BaseContent
from Products.Archetypes.public import registerType

from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.CMFCore import permissions
from Products.CMFCore.utils import getToolByName
from Products.Quills.config import PROJECTNAME

WeblogTopicSchema = BaseSchema.copy() + Schema((
    ImageField('topicImage',
        required=1,
        sizes={'64' : (64,64),},
           widget=ImageWidget(label="Image",
               description="An image for your topic. The image should be 64x64.  If the image is larger it will be scaled down automatically to fit within a 64x64 square."),
        ),
    ),
    marshall=PrimaryFieldMarshaller(),
    )


WeblogTopicSchema['allowDiscussion'].default=0


class WeblogTopic(BaseContent):
    """Weblog Topic"""
    topicImage = ''
    default_topic_image='default-topic-icon.jpg',
    schema = WeblogTopicSchema
    archetype_name = "Topic"
    global_allow = 0
    actions = (
        { 'id': 'view',
          'name': 'View',
          'action': 'string:weblogtopic_view',
          'permissions': (permissions.View,) },
    )

    def setId(self, value):
        "Update any weblog entries using this topic"

        oldid = self.getId()

        BaseContent.setId(self, value)

        path = '/'.join(self.getPhysicalPath()[:-1])
        entries = self.portal_catalog(
            meta_type=['WeblogEntry',],
            path={'query':path, 'level': 0},
            getEntryCategories = oldid,
            )

        for entry in entries:
            o = entry.getObject()
            newcats = []
            for cat in o.getEntryCategories():
                if cat == oldid:
                    newcats.append(value)
                else:
                    newcats.append(cat)
            o.setEntryCategories(newcats)
            o.reindexObject()

    def setTitle(self, value, **kwargs):
        if not value and self.id:
            value = self.id
        else:
            weblog = self.quills_tool.getParentWeblog(self)
            plone_tool = getToolByName(self, 'plone_utils')
            self.setId(plone_tool.normalizeString(value))

        self.getField('title').set(self, value, **kwargs)

    def getLazyEntries(self):
        """Return a list of lazy_maps for all entries in this topic"""
        weblog = self.quills_tool.getParentWeblog(self)
        path = '/'.join(weblog.getPhysicalPath())
        results = self.portal_catalog(meta_type='WeblogEntry',
                path={'query':path, 'level': 0},
                getEntryCategories = { 'query':self.id,
                                       'operator':'and'},
                sort_on = 'effective',
                sort_order = 'reverse',
                review_state = 'published')

        return results


registerType(WeblogTopic, PROJECTNAME)
