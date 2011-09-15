# Intense Healing rune
spell.conjureRune("adura gran", 2265, 4, 240, 15, 1)
spell.targetRune(2265, 15, 1, 3, spell.HEALING_GROUP, enum.EFFECT_MAGIC_BLUE, spell.healTarget(3.184, 5.59, 20, 35))

# Light Healing instant
spell.selfTargetSpell("exura", "Light Healing", 1, 9, 20, spell.HEALING_GROUP, enum.EFFECT_MAGIC_BLUE, spell.healTarget(1.4, 1.795, 8, 11)) # words, icon, level, mana, group, effect, callback, cooldown=1