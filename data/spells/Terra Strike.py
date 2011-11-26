
instant = spell.Spell("Terra Strike", "exori tera", icon=113, group=None)
instant.require(mana=20, level=13, maglevel=0, learned=0, vocations=(1, 5, 2, 6))
instant.cooldowns(2, 2)
instant.targetEffect() # TODO
instant.effects() # TODO