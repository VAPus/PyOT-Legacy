
instant = spell.Spell("Flame Strike", "exori flam", icon=89, group=None)
instant.require(mana=20, level=12, maglevel=0, learned=0, vocations=(1, 2, 5, 6))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO