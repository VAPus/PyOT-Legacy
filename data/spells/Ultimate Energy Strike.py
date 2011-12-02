instant = spell.Spell("Ultimate Energy Strike", "exori max vis", icon=155, group=ATTACK_GROUP)
instant.require(mana=100, level=100, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(30, 4)
instant.targetEffect(callback=spell.damage(4.5, 7.3, 35, 55, ENERGY))
instant.effects() # TODO