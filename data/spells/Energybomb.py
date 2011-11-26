
conjure = spell.Spell("Energybomb", "adevo mas vis", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=880, level=37, maglevel=0, soul=5, learned=0, vocations=(1, 5))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2262, 2))

# Incomplete! Field rune.
rune = spell.Rune(2262, icon=55, count=2, target=TARGET_AREA, group=None)
rune.cooldowns(0, 2)
rune.require(mana=0, level=37, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO