from Products.CMFCore import permissions as cmfpermissions
import Products.Archetypes.public as atapi
import config

def _formatPermissionForType(portal_type):
    return "%s: Add %s" % (config.PROJECTNAME, portal_type)

def initialize():
    permissions = {}
    types = atapi.listTypes(config.PROJECTNAME)
    for atype in  types:
        permission = _formatPermissionForType(atype['portal_type'])
        permissions[atype['portal_type']] = permission
        cmfpermissions.setDefaultRoles(permission, ('Manager','Owner', 'Contributor'))
    ManageTeamMembership = 'Manage team memberships'
    cmfpermissions.setDefaultRoles(ManageTeamMembership, ('Manager',))
    return permissions

View = cmfpermissions.View
AddContent = cmfpermissions.AddPortalContent
EditContent = cmfpermissions.ModifyPortalContent
DeleteContent = cmfpermissions.DeleteObjects
ViewDrafts = 'Quills: View Drafts'
cmfpermissions.setDefaultRoles(ViewDrafts, ('Manager','Owner'))


def getQuillsAddPermissions():
    """Return a sequence of all the 'add' permissions for Quills types.
    """
    qtypes = atapi.listTypes(config.PROJECTNAME)
    perms = []
    for atype in  qtypes:
        permission = _formatPermissionForType(atype['portal_type'])
        perms.append(permission)
    return perms

def unsetupPortalSecurity(portal, out=None):
    pass
