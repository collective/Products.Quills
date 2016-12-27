===============
Products.Quills
===============

Quills is an Enterprise Weblog System for the Plone content management system.
It is designed from the ground up to work well and provide specialized features
for a multi-blog, multi-user environment.

Requires Plone 3.1 or later. Has been tested for compatibility with Plone 4.3.

Newer Replacement: Products.QuillsEnabled:
==========================================

If you are new to Quills, you should probably use Products.QuillsEnabled 
instead of Products.Quills. 

It is a more lightweight and future-proof version that uses
marker interfaces instead of custom portal types. Future development efforts
will focus more on Products.QuillsEnabled then on Products.Quills.

Extensions
==========

There are a few packages that add extra functionality to your Blog.

quills.remoteblogging
    Use your Blog with any Weblog Editor that supports the `MetaWeblog API`_.
    This feature requires the ``Products.MetaWeblogPASPlugin`` product to
    be installed into your Plone site.

    .. _MetaWeblog API: http://www.metaweblogapi.com/


Pitfalls
========

There is a `slight incompatibility`_ with `Quintagroup's Plone
Comments`_ product. To fix it, open the ZMI of your Plone site and go
to the “portal_form_controler”. There select the tab “Actions” and
delete the overide “discussion_reply_form”.

.. _slight incompatibility: http://groups.google.com/group/plone-quills/browse_thread/thread/c03829a8be2c2db2
.. _Quintagroup's Plone Comments: http://pypi.python.org/pypi/quintagroup.plonecomments


Links
=====

Product Homepage
    Visit `https://github.com/collective/Products.Quills`__ to learn more about Quills.

    __ https://github.com/collective/Products.Quills

Mailing List
    Read our mailing list archive at `Google Groups`__, or subscribe to it
    there. To post, write an e-mail to `plone-quills@googlegroups.com`__.
    
    __ http://groups.google.com/group/plone-quills
    __ plone-quills@googlegroups.com

Issue Tracker
    Report bugs and request features by using the `issue tracker`__ on our
    product homepage.

    __ https://github.com/collective/Products.Quills/issues


Code Repository
    You can find the source code in the Plone Collective Repository at
    `https://github.com/collective/Products.Quills/`__.

    __ https://github.com/collective/Products.Quills

