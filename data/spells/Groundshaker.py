instant = spell.Spell("Groundshaker", "exori mas", icon=106, group=ATTACK_GROUP)
instant.require(mana=160, level=33, maglevel=0, learned=0, vocations=(4, 8))
instant.cooldowns(8, 2)
instant.area(AREA_CIRCLE3)
instant.targetEffect(callback=spell.damage(3.184, 5.59, 4, 6, PHYSICAL)) #skill based damage? (x,x, 4, 6) unknown
instant.effects() # TODO