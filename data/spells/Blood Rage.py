
instant = spell.Spell("Blood Rage", "utito tempo", icon=133, group=None)
instant.require(mana=290, level=60, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(2, 3)
instant.targetEffect() # TODO
instant.effects() # TODO