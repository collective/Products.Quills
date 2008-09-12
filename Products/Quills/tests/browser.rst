Quills browser tests
====================

N.B. Much of the generic browser testing has been factored out into
quills/app/tests/browser.rst.  *Only* browser tests that are *specific* to the
Products.Quills implementation (as opposed to Products.QuillsEnabled) should be
in this file.


Here we click ourselves through a Quills instance and check that everything is
in order. First some boilerplate to get our browser up and running:

    >>> self.setRoles(("Contributor",))
    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = False


adding content
**************

    >>> browser.open('http://nohost/plone/weblog/')
    >>> browser.getLink(url='http://nohost/plone/weblog/createObject?type_name=WeblogEntry').click()
    >>> browser.getControl('Title').value = "New entry"
    >>> browser.getControl('Excerpt').value = "A new entry"
    >>> browser.getControl('Text').value = "This is a new entry."
    >>> browser.getControl(name='allowDiscussion:boolean').value = True
    >>> browser.getControl(name='subject_existing_keywords:default:list').value = "fishslapping"
    >>> browser.getControl('Save').click()

Having filled out the form and saved it we should now be viewing our newly baked
entry:

    >>> browser.url
    'http://nohost/plone/weblog/new-entry/weblogentry_view'

However, since we only have the Contributor role, we are not allowed to publish
the item:

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

We also need to enable comments for the entry:

    >>> entry = self.weblog['new-entry']

Now we open the page in a browser:

    >>> browser.open('http://nohost/plone/weblog/new-entry')

The non-archive view has a button to add a comment:

    >>> browser.getControl('Add Comment')
    <SubmitControl name=None type='submit'>

When viewing an entry via its archive url, we still should be able to add a
comment, as well:

    >>> date = entry.getPublicationDate()
    >>> year = str(date.year())
    >>> month = str(date.month()).zfill(2)
    >>> day = str(date.day()).zfill(2)

    >>> browser.open('http://nohost/plone/weblog/%s/%s/%s/new-entry' % (year, month, day))
    >>> browser.getControl('Add Comment').click()

    >>> browser.getControl('Subject').value = "Parrot"
    >>> browser.getControl('Comment').value = "Is dead. Is deceased."

However, currently this still raises an error (eventhough the comment is
actually created). See issue http://plone.org/products/quills/issues/105:

    >> browser.getControl('Save').click()


