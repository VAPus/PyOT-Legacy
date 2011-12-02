instant = spell.Spell("Physical Strike", "exori moe ico", icon=148, group=ATTACK_GROUP)
instant.require(mana=20, level=16, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(2, 2)
instant.targetEffect(callback=spell.damage(1.4, 2.2, 8, 14, PHYSICAL))
instant.effects() # TODO