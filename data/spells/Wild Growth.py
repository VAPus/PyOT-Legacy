
conjure = spell.Spell("Wild Growth", "adevo grav vita", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=600, level=27, maglevel=0, soul=5, learned=0, vocations=(2, 6))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2269, 2))

# Incomplete! Self target rune?
rune = spell.Rune(2269, icon=94, count=2, target=TARGET_TARGET, group=None)
rune.cooldowns(0, 3)
rune.require(mana=0, level=27, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO