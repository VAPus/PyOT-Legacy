
instant = spell.Spell("Intense Healing", "exura gran", icon=2, group=None)
instant.require(mana=70, level=11, maglevel=0, learned=0, vocations=(1, 2, 3, 5, 6, 7))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO