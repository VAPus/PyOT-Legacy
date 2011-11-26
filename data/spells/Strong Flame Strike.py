
instant = spell.Spell("Strong Flame Strike", "exori gran flam", icon=150, group=None)
instant.require(mana=60, level=70, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(8, 2)
instant.targetEffect() # TODO
instant.effects() # TODO