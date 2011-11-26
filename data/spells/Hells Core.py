
instant = spell.Spell("Hells Core", "exevo gran mas flam", icon=24, group=None)
instant.require(mana=1200, level=60, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(40, 4)
instant.targetEffect() # TODO
instant.effects() # TODO