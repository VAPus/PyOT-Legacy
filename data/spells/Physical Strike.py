
instant = spell.Spell("Physical Strike", "exori moe ico", icon=148, group=None)
instant.require(mana=20, level=16, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO