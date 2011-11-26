
instant = spell.Spell("Magic Rope", "exani tera", icon=76, group=None)
instant.require(mana=20, level=9, maglevel=0, learned=0, vocations=(1, 2, 3, 4, 5, 6, 7, 8))
instant.cooldowns(2, 3)
instant.targetEffect() # TODO
instant.effects() # TODO