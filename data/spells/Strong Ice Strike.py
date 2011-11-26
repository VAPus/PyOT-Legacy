
instant = spell.Spell("Strong Ice Strike", "exori gran frigo", icon=152, group=None)
instant.require(mana=60, level=80, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(8, 2)
instant.targetEffect() # TODO
instant.effects() # TODO