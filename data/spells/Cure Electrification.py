instant = spell.Spell("Cure Electrification", "exana vis", icon=146, group=None)
instant.require(mana=30, level=22, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(6, 1)
instant.targetEffect() # TODO
instant.effects() # TODO