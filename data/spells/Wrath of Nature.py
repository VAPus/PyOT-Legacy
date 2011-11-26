
instant = spell.Spell("Wrath of Nature", "exevo gran mas tera", icon=56, group=None)
instant.require(mana=700, level=55, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(40, 4)
instant.targetEffect() # TODO
instant.effects() # TODO