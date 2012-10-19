@register("talkactionFirstWord", "language")
@access("DEVELOPER")

def setLang(creature, text):
	languages = { "norwegian": "nb_NO", "spanish": "es_ES", "english": "en_EN", "polish": "pl_PL" }
	# can't change to english atm, needs a fix
	text.strip()

	if text in languages:
		creature.setLanguage(languages[text])
		creature.message("Your language has been changed to %s" % text, MSG_INFO_DESCR)
	else:
		creature.message("Unrecognized language.", MSG_INFO_DESCR)
	return False