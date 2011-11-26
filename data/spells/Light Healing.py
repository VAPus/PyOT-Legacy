
instant = spell.Spell("Light Healing", "exura", icon=1, group=None)
instant.require(mana=20, level=9, maglevel=0, learned=0, vocations=(1, 2, 3, 5, 6, 7))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO