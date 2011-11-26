
instant = spell.Spell("Whirlwind Throw", "exori hur", icon=107, group=None)
instant.require(mana=40, level=28, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(6, 2)
instant.targetEffect() # TODO
instant.effects() # TODO