
instant = spell.Spell("Front Sweep", "exori min", icon=59, group=None)
instant.require(mana=200, level=70, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(6, 2)
instant.targetEffect() # TODO
instant.effects() # TODO