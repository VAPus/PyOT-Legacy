import game.spell as spell
import game.enum as enum

spell.conjureRune("adura gran", 2265, 4, 240, 15, 1)
spell.targetRune(2265, 15, 1, 3, spell.HEALING_GROUP, enum.EFFECT_MAGIC_BLUE, spell.healTarget(3.184, 5.59, 20, 35))