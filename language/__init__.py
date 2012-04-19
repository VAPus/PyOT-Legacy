# Setup
import os, os.path, glob
import __builtin__
import gettext
import config

__all__ = []
LANGUAGES = {}

if config.enableTranslations:
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

        return creature.l(message)

    def _lp(creature, singular, plural, n):
        if type(creature) == str:
            return LANGUAGES[creature].ngettext(singular, plural, n)
        else:
            return creature.lp(singular, plural, n)

    def _pgettext(self, contexts, message):
        index = 0
        found = False
        tmsg = None
        while not found:
            ctxt_msg_id = self.CONTEXT % (contexts[index], message)
            missing = object()
            tmsg = self._catalog.get(ctxt_msg_id, missing)
            if tmsg is missing:
                if len(contexts) <= index+1:
                    tmsg = self.gettext(message)
                    found = True
                else:
                    index += 1
            else:
                found = True
        # Encode the Unicode tmsg back to an 8-bit string, if possible
        if self._output_charset:
            return tmsg.encode(self._output_charset)
        elif self._charset:
            return tmsg.encode(self._charset)
        return tmsg

    def _npgettext(self, contexts, msgid1, msgid2, n):
        index = 0
        found = False
        tmsg = None
        while not found:
            ctxt_msg_id = self.CONTEXT % (contexts[index], msgid1)
            try:
                tmsg = self._catalog[(ctxt_msg_id, self.plural(n))]
                if self._output_charset:
                    tmsg = tmsg.encode(self._output_charset)
                elif self._charset:
                    tmsg = tmsg.encode(self._charset)
                found = True
            except KeyError:
                if len(contexts) <= index+1:
                    tmsg = self.ngettext(msgid1, msgid2, n)
                    found = True
                else:
                    index += 1
        return tmsg

else:
    _l = lambda c,m: m
    _lp = lambda c,s,p,n: p if n > 1 else s
    _pgettext = lambda c,m: m
    _npgettext = lambda c,s,p,n: p if n > 1 else s

__builtin__._l = _l
__builtin__._lp = _lp
__builtin__._ = lambda m: m
