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

PROJECTNAME = "Quills"
MY_GS_PROFILE = "Products.%s" % (PROJECTNAME,)
DEPENDENCIES = ()
# Toggle to determine whether a 'topic_images' folder should be created
# automatically in each new Weblog instance.
CREATE_TOPIC_IMAGES_FOLDERS = True
TOPIC_IMAGE_FOLDER_ID = 'topic_images'
CREATE_UPLOAD_FOLDERS = True
UPLOAD_FOLDER_ID = 'uploads'
