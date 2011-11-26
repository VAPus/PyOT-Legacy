
instant = spell.Spell("Ultimate Flame Strike", "exori max flam", icon=154, group=None)
instant.require(mana=100, level=90, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(30, 4)
instant.targetEffect() # TODO
instant.effects() # TODO