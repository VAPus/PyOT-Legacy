instant = spell.Spell("Strong Flame Strike", "exori gran flam", icon=150, group=ATTACK_GROUP)
instant.require(mana=60, level=70, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(8, 2)
instant.targetEffect(callback=spell.damage(2.8, 4.4, 16, 28, FIRE))
instant.effects() # TODO