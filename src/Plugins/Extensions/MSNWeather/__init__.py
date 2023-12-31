from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext

__version__ = "1.2"

PluginLanguageDomain = "MSNWeather"
PluginLanguagePath = "Extensions/MSNWeather/locale"


def localeInit():
	gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
	t = gettext.dgettext(PluginLanguageDomain, txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t


localeInit()
language.addCallback(localeInit)
