
instant = spell.Spell("Wound Cleansing", "exura ico", icon=123, group=None)
instant.require(mana=40, level=10, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(1, 1)
instant.targetEffect() # TODO
instant.effects() # TODO