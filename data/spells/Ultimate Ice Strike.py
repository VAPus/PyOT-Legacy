
instant = spell.Spell("Ultimate Ice Strike", "exori max frigo", icon=156, group=None)
instant.require(mana=100, level=100, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(30, 4)
instant.targetEffect() # TODO
instant.effects() # TODO