
instant = spell.Spell("Strong Haste", "utani gran hur", icon=39, group=None)
instant.require(mana=100, level=20, maglevel=0, learned=0, vocations=(1, 2, 5, 6))
instant.cooldowns(2, 3)
instant.targetEffect() # TODO
instant.effects() # TODO