# A pretty conjure test
import game.spell as spell

spell.conjureRune("Fire Field Rune", "adevo grav flam", 2301, 25, 240, 15, 1, makeCount=3)
spell.fieldRune(2301, 15, 1, 25, spell.ATTACK_GROUP, spell.AREA_ONE, spell.makeField(1492)) # rune, level, mlevel, icon, group, area, callback