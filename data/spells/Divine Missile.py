
instant = spell.Spell("Divine Missile", "exori san", icon=122, group=None)
instant.require(mana=20, level=40, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO