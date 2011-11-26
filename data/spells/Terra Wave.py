
instant = spell.Spell("Terra Wave", "exevo tera hur", icon=120, group=None)
instant.require(mana=210, level=38, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO