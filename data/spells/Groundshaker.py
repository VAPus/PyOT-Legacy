
instant = spell.Spell("Groundshaker", "exori mas", icon=106, group=None)
instant.require(mana=160, level=33, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(8, 2)
instant.targetEffect() # TODO
instant.effects() # TODO