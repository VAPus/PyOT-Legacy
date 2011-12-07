instant = spell.Spell("Intense Wound Cleansing", "exura gran ico", icon=158, group=HEALING_GROUP)
instant.require(mana=200, level=80, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(180, 1)
instant.targetEffect() # TODO
instant.effects() # TODO