instant = spell.Spell("Cure Bleeding", "exana kor", icon=144, group=HEALING_GROUP)
instant.require(mana=30, level=30, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(6, 1)
instant.targetEffect() # TODO
instant.effects() # TODO