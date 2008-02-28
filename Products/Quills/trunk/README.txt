About
=====

Quills is a Weblog System for the Plone content management system.  It is
designed from the ground up to work well and provide specialized features for a
multi-blog, multi-user environment.


Doc file
========

   A doc file has been started in the doc subdirectory.


Dependencies
============

Requires
--------

  o Zope 2.10.4+

  o Plone 3

  o In you Products directory:

    o basesyndication

    o fatsyndication

  o In you lib/python/ (see note below)

    o quills.core

    o quills.app

Optional
--------

  o Trackback support:

    o quills.trackback (lib/python/)

    o ATTrackback (Products)

    o QuillsTrackback (Products)

  o Remote blogging support - which is currently only via MetaWeblogAPI:

    o quills.remoteblogging (lib/python/)

    o QuillsRemoteBloggin (Products)

    o MetaWeblogPASPlugin (Products)

More specifically, quills.core and quills.app are required to be available
from your python path (i.e. probably lib/python/quills/core).  For a basic
installation, that should be enough (although I haven't tested that extensively
so do let me know if I'm wrong on that).

MetaWeblogPASPlugin can be found in the PASPlugins directory in the collective.


Acknowledgements
================

Google's 'Summer of Code' supported me (Tim Hicks) for several months in 2007
to further develop the Quills product - for which I'm very grateful.


Resources
=========

    Development Homepage:  http://plone.org/products/quills/
    Bug Tracker:           http://plone.org/products/quills/issues/
    Mailing List:          http://lists.etria.com/cgi-bin/mailman/listinfo/quills-dev
    Subversion Repository: https://svn.plone.org/svn/collective/Quills/


Other Zope/Plone Weblog Products
================================

Plone Compatible:
    CMFWeblog   http://www.sf.net/projects/collective/
    SimpleBlog  http://www.sf.net/projects/collective/
    COREBlog    http://coreblog.org/
    EasyBlog    http://plone.org/products/easyblog/

