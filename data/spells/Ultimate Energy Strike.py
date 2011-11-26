
instant = spell.Spell("Ultimate Energy Strike", "exori max vis", icon=155, group=None)
instant.require(mana=100, level=100, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(30, 4)
instant.targetEffect() # TODO
instant.effects() # TODO