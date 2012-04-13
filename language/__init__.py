# Setup
import os, os.path, glob
import __builtin__
import gettext
import config

__all__ = []
LANGUAGES = {}

base = os.path.split(__file__)[0] # Remove the ending of the paths!
    
for mod in glob.glob("%s/*.mo" % base):
    modm = mod.split(os.sep)[-1].replace('.mo', '')
    if modm == "__init__":
        continue

    __all__.append(modm)

# Initialize GNUTranslations (regular gettext is singel language only :()
for language in __all__:
    LANGUAGES[language] = gettext.GNUTranslations(open("%s/%s.mo" % (base, language)))
    

# Functions
if LANGUAGES:
    def _l(creature, message):
        if type(creature) == str:
            return LANGUAGES[creature].gettext(message)
        elif creature.isPlayer():
            return LANGUAGES[creature.data["language"] or config.defaultLanguage].gettext(message)
        else:
            return message

    def _lp(creature, singular, plural, n):
        if type(creature) == str:
            return LANGUAGES[creature].ngettext(singular, plural, n)
        elif creature.isPlayer():
            return LANGUAGES[creature.data["language"] or config.defaultLanguage].ngettext(singular, plural, n)
        elif n > 1:
            return plural
        else:
            return singular
else:
    _l = lambda c,m: m
    _lp = lambda c,s,p,n: p if n > 1 else s
    
__builtin__._l = _l
__builtin__._lp = _lp