instant = spell.Spell("Ultimate Ice Strike", "exori max frigo", icon=156, group=ATTACK_GROUP)
instant.require(mana=100, level=100, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(30, 4)
instant.targetEffect(callback=spell.damage(4.5, 7.3, 35, 55, ICE))
instant.effects() # TODO