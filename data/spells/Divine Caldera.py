
instant = spell.Spell("Divine Caldera", "exevo mas san", icon=124, group=None)
instant.require(mana=140, level=50, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(4, 2)
instant.targetEffect() # TODO
instant.effects() # TODO