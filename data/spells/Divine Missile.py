instant = spell.Spell("Divine Missile", "exori san", icon=122, target=TARGET_TARGET, group=ATTACK_GROUP)
instant.require(mana=20, level=40, maglevel=0, learned=0, vocations=(3, 7))
instant.cooldowns(2, 2)
instant.area(AREA_WAVE1)
instant.targetEffect(callback=spell.damage(1.9, 3, 8, 18, HOLY))
instant.effects() # TODO