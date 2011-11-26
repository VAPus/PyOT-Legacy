
instant = spell.Spell("Ice Wave", "exevo frigo hur", icon=121, group=None)
instant.require(mana=25, level=18, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO