
instant = spell.Spell("Energy Wave", "exevo vis hur", icon=13, group=None)
instant.require(mana=170, level=38, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(8, 2)
instant.targetEffect() # TODO
instant.effects() # TODO