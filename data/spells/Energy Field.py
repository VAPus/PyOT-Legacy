
conjure = spell.Spell("Energy Field", "adevo grav vis", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=320, level=18, maglevel=0, soul=2, learned=0, vocations=(1, 2, 5, 6))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2277, 3))

# Incomplete! Field rune.
rune = spell.Rune(2277, icon=27, count=3, target=TARGET_AREA, group=None)
rune.cooldowns(0, 2)
rune.require(mana=0, level=18, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO