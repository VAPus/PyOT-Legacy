
instant = spell.Spell("Fierce Berserk", "exori gran", icon=105, group=None)
instant.require(mana=340, level=90, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(6, 2)
instant.targetEffect() # TODO
instant.effects() # TODO