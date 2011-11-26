
instant = spell.Spell("Charge", "utani tempo hur", icon=131, group=None)
instant.require(mana=100, level=25, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(2, 3)
instant.targetEffect() # TODO
instant.effects() # TODO