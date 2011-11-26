
instant = spell.Spell("Energy Beam", "exevo vis lux", icon=22, group=None)
instant.require(mana=40, level=23, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(4, 2)
instant.targetEffect() # TODO
instant.effects() # TODO