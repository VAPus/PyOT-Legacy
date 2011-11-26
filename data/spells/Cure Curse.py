
instant = spell.Spell("Cure Curse", "exana mort", icon=147, group=None)
instant.require(mana=40, level=80, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO