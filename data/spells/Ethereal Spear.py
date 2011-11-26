
instant = spell.Spell("Ethereal Spear", "exori con", icon=111, group=None)
instant.require(mana=25, level=23, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO