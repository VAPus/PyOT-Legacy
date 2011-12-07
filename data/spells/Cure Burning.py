instant = spell.Spell("Cure Burning", "exana flam", icon=145, group=HEALING_GROUP)
instant.require(mana=30, level=30, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO