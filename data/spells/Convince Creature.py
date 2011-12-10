conjure = spell.Spell("Convince Creature", "adeta sio", icon=23, group=SUPPORT_GROUP)
conjure.require(mana=200, level=16, maglevel=0, soul=3, learned=0, vocations=(2, 6))
conjure.use(2260)
conjure.cooldowns(0, 3)
conjure.targetEffect(callback=spell.conjure(2290, 1))

# Incomplete! Target rune.
rune = spell.Rune(2290, icon=12, count=1, target=TARGET_TARGET, group=SUPPORT_GROUP) #group wrong?
rune.cooldowns(0, 3)
rune.require(mana=0, level=16, maglevel=0)
rune.targetEffect() # TODO
rune.effects() # TODO