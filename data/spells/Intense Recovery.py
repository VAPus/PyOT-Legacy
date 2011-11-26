
instant = spell.Spell("Intense Recovery", "utura gran", icon=160, group=None)
instant.require(mana=165, level=100, maglevel=0, learned=0, vocations=(4, 8, 3, 7))
instant.cooldowns(60, 1)
instant.targetEffect() # TODO
instant.effects() # TODO