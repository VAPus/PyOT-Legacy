
instant = spell.Spell("Protect Party", "utamo mas sio", icon=127, group=None)
instant.require(mana=90, level=32, maglevel=0, learned=0, vocations=(7,))
instant.cooldowns(2, 3)
instant.targetEffect() # TODO
instant.effects() # TODO