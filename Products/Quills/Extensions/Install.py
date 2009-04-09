# Standard library imports
from StringIO import StringIO

# quills imports
from Products.Quills import config
from quills.app.setuphandlers import setup_gs_profiles

import transaction

# The install method is gone! Everything that needs to done in code
# is in module Products.Quills.setuphandlers now. If you must (you don't)
# re-add the install method, make sure to load the GS profile of
# Products.Quills there. QuickInstaller *will not load* the profile by itself!

    
def uninstall(self):
    """QuickInstaller uninstall handler for Quills.

    Unfortunately, the QuickInstaller will not execute extension profiles for 
    uninstalling. That's why we have to do it on our own. All other uninstalling
    is done by profile, either declarative or as code in module 
    ``setuphandlers``.
    """
    out = StringIO()
    setup_gs_profiles(self, (config.MY_GS_PROFILE + ":uninstall",), out)
    print >> out, u"Successfully uninstalled %s." % config.PROJECTNAME
    return out.getvalue()

