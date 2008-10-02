#!/bin/sh

# Synchronise the quills.pot with the templates.
# Also merge it with generated.pot, which includes the items
# from the .py files.
i18ndude rebuild-pot --pot i18n/quills.pot --create quills --merge i18n/generated.pot .

# Synchronise the resulting quills.pot with the .po files
i18ndude sync --pot i18n/quills.pot i18n/quills*.po

# Synchronise the plone*.po files with the hand-made plone-quills.pot
# This one is used for workflow name translations, content type names,
# etc.
i18ndude sync --pot i18n/plone-quills.pot i18n/plone*.po
