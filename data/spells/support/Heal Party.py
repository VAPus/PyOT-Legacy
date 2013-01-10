instant = spell.Spell("Heal Party", "utura mas sio", group=SUPPORT_GROUP)
instant.require(level=32, maglevel=0, learned=0, vocations=(3, 5))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO