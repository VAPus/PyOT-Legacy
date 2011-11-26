
instant = spell.Spell("Divine Healing", "exura san", icon=125, group=None)
instant.require(mana=160, level=35, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO