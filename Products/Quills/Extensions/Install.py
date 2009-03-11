# Standard library imports
from StringIO import StringIO

# quills imports
from Products.Quills import config
from quills.app.setuphandlers import addNewDiscussionReplyFormAction
from quills.app.setuphandlers import delNewDiscussionReplyFormAction


def install(self):
    """Install Quills.
    This method is basically unnecessary in that most of it has been moved to
    Products.Quills.setuphandlers. However, in order to support uninstalling, we
    need the QI tool to pickup the uninstall function below that cleans up our
    'discussion_reply_form' form controller action. For symmetry, I'm therefore
    placing the set up of that action here.

    N.B. Think *very* carefully before you place any more code here. It should
    probably be in one of the setuphandlers modules (i.e. in Products.Quills or
    quills.app).
    """
    out = StringIO()
    addNewDiscussionReplyFormAction(self, out)
    print >> out, u"Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()

def uninstall(self):
    """Uninstall Quills.
    """
    out = StringIO()
    delNewDiscussionReplyFormAction(self, out)
    print >> out, u"Successfully uninstalled %s." % config.PROJECTNAME
    return out.getvalue()

