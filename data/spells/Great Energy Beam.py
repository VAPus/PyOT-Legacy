
instant = spell.Spell("Great Energy Beam", "exevo gran vis lux", icon=23, group=None)
instant.require(mana=110, level=29, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(6, 2)
instant.targetEffect() # TODO
instant.effects() # TODO