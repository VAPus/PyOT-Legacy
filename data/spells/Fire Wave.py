
instant = spell.Spell("Fire Wave", "exevo flam hur", icon=19, group=None)
instant.require(mana=25, level=18, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(4, 2)
instant.targetEffect() # TODO
instant.effects() # TODO