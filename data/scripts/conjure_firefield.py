# A pretty conjure test
import game.spell as spell
import game.scriptsystem as scriptsystem

scriptsystem.get("talkaction").reg(*spell.conjureRune("adevo grav flam", 2301, 25, 240, 15, 1, makeCount=3))