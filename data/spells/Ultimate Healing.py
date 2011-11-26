
instant = spell.Spell("Ultimate Healing", "exura vita", icon=3, group=None)
instant.require(mana=160, level=20, maglevel=0, learned=0, vocations=(1, 2, 5, 6))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO