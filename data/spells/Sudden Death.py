
conjure = spell.Spell("Sudden Death", "adori gran mort", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=985, level=45, maglevel=0, soul=5, learned=0, vocations=(1, 5))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2268, 3))

# Incomplete! Target rune.
rune = spell.Rune(2268, icon=21, count=3, target=TARGET_TARGET, group=None)
rune.cooldowns(0, 2)
rune.require(mana=0, level=45, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO