
instant = spell.Spell("Strong Ice Wave", "exevo gran frigo hur", icon=43, group=None)
instant.require(mana=170, level=40, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(8, 2)
instant.targetEffect() # TODO
instant.effects() # TODO