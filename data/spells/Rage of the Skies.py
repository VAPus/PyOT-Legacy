
instant = spell.Spell("Rage of the Skies", "exevo gran mas vis", icon=119, group=None)
instant.require(mana=650, level=55, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(40, 4)
instant.targetEffect() # TODO
instant.effects() # TODO