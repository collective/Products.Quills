# Zope imports
from zope.interface import implements
from zope.formlib import form

# Quills imports
from quills.core.browser.weblogconfig import WeblogConfigEditForm
from quills.core.browser.weblogconfig import WeblogConfigAnnotations
from quills.app.interfaces import IWeblogEnhancedConfiguration
from quills.app.interfaces import IStateAwareWeblogConfiguration


class StateAwareAwareWeblogConfig(WeblogConfigAnnotations):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogEnhancedConfiguration, StateAwareWeblogConfig)
    True
    """

    implements(IWeblogEnhancedConfiguration)

    # N.B. We just provide default_type here directly as it should not be ttw-
    # configurable - it should never change.
    default_type = 'WeblogEntry'

    def _get_published_states(self):
        return self._config.get('published_states', ['published',])
    def _set_published_states(self, value):
        self._config['published_states'] = value
    published_states = property(_get_published_states, _set_published_states)

    def _get_draft_states(self):
        return self._config.get('draft_states', ['private',])
    def _set_draft_states(self, value):
        self._config['draft_states'] = value
    draft_states = property(_get_draft_states, _set_draft_states)


class StateAwareWeblogConfigEditForm(WeblogConfigEditForm):
    """Edit form for weblog view configuration.
    """

    # N.B. We only ask for fields for IStateAwareWeblogConfiguration because we
    # don't want ttw ui for default_type.
    form_fields = form.Fields(IStateAwareWeblogConfiguration)
    label = u'Weblog View Configuration'

    def setUpWidgets(self, ignore_request=False):
        self.adapters = {}
        wvconfig = IStateAwareWeblogConfiguration(self.context)
        self.widgets = form.setUpEditWidgets(
            self.form_fields, self.prefix, wvconfig, self.request,
            adapters=self.adapters, ignore_request=ignore_request
            )

    @form.action("submit")
    def submit(self, action, data):
        """
        """
        wvconfig = IStateAwareWeblogConfiguration(self.context)
        form.applyChanges(wvconfig, self.form_fields, data)
        msg = 'Configuration saved.'
        IStatusMessage(self.request).addStatusMessage(msg, type='info')
