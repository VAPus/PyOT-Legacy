
conjure = spell.Spell("Explosion", "adevo mas hur", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=570, level=31, maglevel=0, soul=3, learned=0, vocations=(1, 2, 5, 6))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2313, 6))

# Incomplete! Field rune.
rune = spell.Rune(2313, icon=18, count=6, target=TARGET_AREA, group=None)
rune.cooldowns(0, 2)
rune.require(mana=0, level=31, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO