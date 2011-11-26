
instant = spell.Spell("Ultimate Terra Strike", "exori max tera", icon=157, group=None)
instant.require(mana=100, level=90, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(30, 4)
instant.targetEffect() # TODO
instant.effects() # TODO