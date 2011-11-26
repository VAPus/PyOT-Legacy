
instant = spell.Spell("Lightning", "exori amp vis", icon=149, group=None)
instant.require(mana=160, level=55, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(8, 2)
instant.targetEffect() # TODO
instant.effects() # TODO