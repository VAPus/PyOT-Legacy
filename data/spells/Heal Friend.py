
instant = spell.Spell("Heal Friend", "exura sio", icon=84, group=None)
instant.require(mana=140, level=18, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO