instant = spell.Spell("Ice Strike", "exori frigo", icon=112, group=ATTACK_GROUP)
instant.require(mana=20, level=15, maglevel=0, learned=0, vocations=(1, 5, 2, 6))
instant.cooldowns(2, 2)
instant.targetEffect(callback=spell.damage(1.4, 2.2, 8, 14, ICE))
instant.effects() # TODO