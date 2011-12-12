instant = spell.Spell("Swift Foot", "utamo tempo san", icon=134, group=SUPPORT_GROUP)
instant.require(mana=400, level=55, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(2, 10)
instant.targetEffect() # TODO
instant.effects() # TODO