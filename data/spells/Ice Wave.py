instant = spell.Spell("Ice Wave", "exevo frigo hur", icon=121, group=ATTACK_GROUP)
instant.require(mana=25, level=18, maglevel=0, learned=0, vocations=(2, 6))
instant.cooldowns(2, 2)
instant.area(AREA_WAVE4)
instant.targetEffect(callback=spell.damage(0.8, 2, 5, 12, ICE))
instant.effects() # TODO