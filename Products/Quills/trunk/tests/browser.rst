Quills browser tests
====================

Here we klick ourselves through a Quills instance and check that everything is in order. First some boilerplate to get our browser up and running:

    >>> self.setRoles(("Contributor",))
    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = False
    >>> self.weblog.addEntry("Blog entry", "Just for testing", "Nothing to see.", \
    ... ['fishslapping'], id="entry")
    <WeblogEntry at /plone/weblog/entry>

    >>> self.portal.weblog.entry.publish()
    >>> browser.open('http://nohost/plone/weblog/')

portlets
********

Viewing the blog we should get a few portlets. authors, recent entries and the tag cloud:

    >>> browser.contents
    '...<dl class="portlet portletWeblogAuthors"...'

    >>> browser.contents
    '...<dl class="portlet portletRecentEntries"...'

    >>> browser.contents
    '...<dl class="portlet portletRecentComments"...'

    >>> browser.contents
    '...<dl class="portlet portletWeblogArchive"...'

    >>> browser.contents
    '...<dl class="portlet portletTagCloud"...
     ...<a...href="http://nohost/plone/weblog/topics/fishslapping"...
     ...fishslapping</a>...'

And since we're authenticated as Contributor, we also get the admin portlet:

    >>> browser.contents
    '...<dl class="portlet portletWeblogAdmin"...'

And last but not least, the Quills portlet:

    >>> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'


feed links
**********

When viewing a blog, there should be links to its feeds. We expect atom, rss 2.0 and rdf 1.0 and 1.1:

    >>> browser.contents
    '...<link...rel="alternate"...
     ...type="application/atom+xml"...
     ...title="Atom feed"...
     ...http://nohost/plone/weblog/atom.xml...'

    >>> browser.contents
    '...<link...rel="alternate"...
     ...type="application/rss+xml"...
     ...title="RSS 2.0 feed"...
     ...http://nohost/plone/weblog/rss.xml...'

    >>> browser.contents
    '...<link ...http://nohost/plone/weblog/feed11.rdf...'

    >>> browser.contents
    '...<link ...http://nohost/plone/weblog/feed.rdf...'

the same links should also be present when viewing an entry:

    >>> browser.open('http://nohost/plone/weblog/entry')
    >>> browser.contents
    '...<link...rel="alternate"...
     ...type="application/atom+xml"...
     ...title="Atom feed"...
     ...http://nohost/plone/weblog/atom.xml...'

    >>> browser.contents
    '...<link...rel="alternate"...
     ...type="application/rss+xml"...
     ...title="RSS 2.0 feed"...
     ...http://nohost/plone/weblog/rss.xml...'

    >>> browser.contents
    '...<link ...http://nohost/plone/weblog/feed11.rdf...'

    >>> browser.contents
    '...<link ...http://nohost/plone/weblog/feed.rdf...'


archive
*******

having one published entry also gives us an archive:

    >>> date = self.portal.weblog.entry.getPublicationDate()
    >>> year = str(date.year())
    >>> month = str(date.month()).zfill(2)
    >>> day = str(date.day()).zfill(2)

    >>> browser.open('http://nohost/plone/weblog/%s/' % year)
    >>> browser.contents
    '...<h1>Year...</h1>...'

Viewing the archive should still give us a context where the portlets are rendered. We test this by checking for the quillslinks portlet:

    >> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'

    >>> browser.open('http://nohost/plone/weblog/%s/%s/' % (year, month))
    >>> browser.contents
    '...<h1>Month...</h1>...'

    >> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'

    >>> browser.open('http://nohost/plone/weblog/%s/%s/%s/' % (year, month, day))
    >>> browser.contents
    '...Blog entry...'

    >>> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'

topics
******

    >>> browser.open('http://nohost/plone/weblog/topics')
    >>> '<div id="weblogtopics">' in browser.contents
    True

Viewing the topics overview should still give us a context where the portlets are rendered. We test this by checking for the quillslinks portlet:

    >> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'


Having a published entry with the topic 'fishslapping' gives us the following:

    >>> browser.open('http://nohost/plone/weblog/topics/fishslapping')
    >>> '<div id="topic-summary">' in browser.contents
    True

    >>> 'Blog entry' in browser.contents
    True

    >>> '<h1>fishslapping</h1>' in browser.contents
    True

Viewing the topic view should still give us a context where the portlets are rendered. We test this by checking for the quillslinks portlet:

    >>> browser.contents
    '...<dl class="portlet portletQuillsLinks"...'


author topics
*************

    >>> browser.open('http://nohost/plone/weblog/authors')
    >>> '<h1 class="documentFirstHeading">Weblog Authors</h1>' in browser.contents
    True

    >>> '<a href="http://nohost/plone/weblog/authors/portal_owner">portal_owner</a>' in browser.contents
    True

adding content
**************

    >>> browser.open('http://nohost/plone/weblog/')
    >>> browser.getLink(url='http://nohost/plone/weblog/createObject?type_name=WeblogEntry').click()
    >>> browser.getControl('Title').value = "New entry"
    >>> browser.getControl('Excerpt').value = "A new entry"
    >>> browser.getControl('Text').value = "This is a new entry."
    >>> browser.getControl(name='allowDiscussion:boolean').value = True
    >>> browser.getControl(name='subject_existing_keywords:list').value = ["fishslapping",]
    >>> browser.getControl('Save').click()

Having filled out the form and saved it we should now be viewing our newly baked entry:

    >>> browser.url
    'http://nohost/plone/weblog/new-entry/weblogentry_view'

However, since we only have the Contributor role, we are not allowed to publish the item:

    >>> browser.getLink('Publish')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

But we can submit the entry for publication:

    >>> browser.getLink('Submit').click()

If we additionally grant the `Reviewer` role we can publish the new entry:

    >>> self.setRoles(("Contributor", "Reviewer"))
    >>> browser.reload()
    >>> browser.getLink('Publish').click()
    
comments
********

By default we even need the `Manager` role to add comments:

    >>> self.setRoles(("Contributor", "Reviewer", "Manager"))
    >>> browser.reload()
    >>> browser.url
    'http://nohost/plone/weblog/new-entry/weblogentry_view'

The non-archive view has a button to add a comment:

    >>> browser.getControl('Add Comment')
    <SubmitControl name=None type='submit'>

When viewing an entry via its archive url, we still should be able to add a comment, as well:

    >>> browser.open('http://nohost/plone/weblog/%s/%s/%s/new-entry' % (year, month, day))
    >>> browser.getControl('Add Comment').click()

    >>> browser.getControl('Subject').value = "Parrot"
    >>> browser.getControl('Comment').value = "Is dead. Is deceased."

However, currently this still raises an error (eventhough the comment is actually created). See issue http://plone.org/products/quills/issues/105:

    >> browser.getControl('Save').click()


configure blog
**************

Since we're logged in as Manager we have access to the configuration tab:

    >>> browser.open('http://nohost/plone/weblog')
    >>> browser.getLink('Configure').click()
    >>> browser.url
    'http://nohost/plone/weblog/config_view'

But we can also reach this screen via the management portlet:

    >>> browser.getLink('Configure Blog').click()
    >>> browser.url
    'http://nohost/plone/weblog/config_view'
