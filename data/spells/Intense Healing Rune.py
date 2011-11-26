
conjure = spell.Spell("Intense Healing Rune", "adura gran", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=240, level=15, maglevel=0, soul=2, learned=0, vocations=(2, 6))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2265, 1))

# Incomplete! Target rune.
rune = spell.Rune(2265, icon=3, count=1, target=TARGET_TARGET, group=None)
rune.cooldowns(0, 1)
rune.require(mana=0, level=15, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO