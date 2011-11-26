
instant = spell.Spell("Salvation", "exura gran san", icon=36, group=None)
instant.require(mana=210, level=60, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO