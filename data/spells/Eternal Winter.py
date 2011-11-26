
instant = spell.Spell("Eternal Winter", "exevo gran mas frigo", icon=118, group=None)
instant.require(mana=1050, level=60, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(40, 4)
instant.targetEffect() # TODO
instant.effects() # TODO