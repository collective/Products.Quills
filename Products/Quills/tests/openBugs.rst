Quills Open Bugs
================

This file contains tests for bugs not yet fixed.


Issue #142: Title of weblog entry cannot be a whole number
----------------------------------------------------------

Entering a number as the title of a blog entry will make Quills
interpret the entry id as an archive URL.

Quills' WeblogTraverser is the culprit, let get it.

    >>> from zope.component import queryMultiAdapter
    >>> from zope.publisher.interfaces import IPublishTraverse
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> traverse = queryMultiAdapter((self.weblog, request),
    ...                              IPublishTraverse)

We have no offending entry yet, so it will be perfectly fine if we get the 
archive of year 10 AD.

    >>> from quills.app.archive import YearArchive
    >>> isinstance(traverse.publishTraverse(request, '10'), YearArchive)
    True

But what if we happen to add an entry that gets a id that could be mistaken
for a year? There is no clear answer to that, but for archives we can configure
an URL prefix like archive/2008/12/21. So will suppose here to get a weblog
entry to make us remember the bug.

    >>> entry = self.weblog.addEntry("10", "Alas!",
    ...              "This not part of the archive!")
    >>> from quills.core.interfaces import IWeblogEntry
    >>> IWeblogEntry.providedBy( traverse.publishTraverse(request, '10') )
    True

I would be probably best to filter offending ids.