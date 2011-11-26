
instant = spell.Spell("Berserk", "exori", icon=80, group=None)
instant.require(mana=115, level=35, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(4, 2)
instant.targetEffect() # TODO
instant.effects() # TODO