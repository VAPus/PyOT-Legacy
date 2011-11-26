
instant = spell.Spell("Strong Energy Strike", "exori gran vis", icon=151, group=None)
instant.require(mana=60, level=80, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(8, 2)
instant.targetEffect() # TODO
instant.effects() # TODO