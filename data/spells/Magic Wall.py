
conjure = spell.Spell("Magic Wall", "adevo grav tera", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=750, level=32, maglevel=0, soul=5, learned=0, vocations=(1, 5))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2293, 3))

# Incomplete! Self target rune?
rune = spell.Rune(2293, icon=86, count=3, target=TARGET_TARGET, group=None)
rune.cooldowns(0, 3)
rune.require(mana=0, level=32, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO