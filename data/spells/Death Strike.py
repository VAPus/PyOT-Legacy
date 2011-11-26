
instant = spell.Spell("Death Strike", "exori mort", icon=87, group=None)
instant.require(mana=20, level=16, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO