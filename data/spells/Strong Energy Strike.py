instant = spell.Spell("Strong Energy Strike", "exori gran vis", icon=151, target=TARGET_TARGET, group=ATTACK_GROUP)
instant.require(mana=60, level=80, maglevel=0, learned=0, vocations=(1, 5))
instant.cooldowns(8, 2)
instant.range(4)
instant.area(AREA_WAVE1)
instant.targetEffect(callback=spell.damage(2.8, 4.4, 16, 28, ENERGY))
instant.effects(area=EFFECT_ENERGYAREA, shoot=ANIMATION_ENERGY)