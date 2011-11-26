
instant = spell.Spell("Mass Healing", "exura gran mas res", icon=82, group=None)
instant.require(mana=150, level=36, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO