
conjure = spell.Spell("Fire Wall", "adevo mas grav flam", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=780, level=33, maglevel=0, soul=3, learned=0, vocations=(1, 2, 5, 6))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2303, 3))

# Incomplete! Field rune.
rune = spell.Rune(2303, icon=25, count=3, target=TARGET_AREA, group=None)
rune.cooldowns(0, 2)
rune.require(mana=0, level=33, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO