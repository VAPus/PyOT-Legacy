
instant = spell.Spell("Strong Ethereal Spear", "exori gran con", icon=57, group=None)
instant.require(mana=55, level=90, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(8, 2)
instant.targetEffect() # TODO
instant.effects() # TODO