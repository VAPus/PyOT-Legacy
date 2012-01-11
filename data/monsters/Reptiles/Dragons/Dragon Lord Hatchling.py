dragon_lord_hatchling = game.monster.genMonster("Dragon Lord Hatchling", (8, 5980), "a dragon lord hatchling")
dragon_lord_hatchling.setHealth(750)
dragon_lord_hatchling.bloodType(color="blood")
dragon_lord_hatchling.setDefense(armor=30, fire=0, earth=0.75, energy=1.05, ice=1.1, holy=1, death=1, physical=1, drown=1)
dragon_lord_hatchling.setExperience(645)
dragon_lord_hatchling.setSpeed(200)
dragon_lord_hatchling.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=80)
dragon_lord_hatchling.walkAround(energy=1, fire=0, poison=1)
dragon_lord_hatchling.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
dragon_lord_hatchling.voices("Fchu?", "Rooawwrr")
dragon_lord_hatchling.loot( (2148, 100, 169), ("dragon ham", 69.75), ("green mushroom", 0.5), ("mana potion", 0.5), ("magma boots", 0.0025) )

dfwave = spell.Spell("drag fwave", target=TARGET_AREA)
dfwave.area(AREA_WAVE7)
dfwave.targetEffect(callback=spell.damage(1, 1, 90, 125, FIRE))
dfwave.effects(area=EFFECT_HITBYFIRE)
 
dragon_lord_hatchling.regMelee(90)
dragon_lord_hatchling.regTargetSpell(2305, 55, 105, check=chance(20)) #firebomb
dragon_lord_hatchling.regTargetSpell("drag fwave", check=chance(20))
dragon_lord_hatchling.regTargetSpell(2304, 100, 200, check=chance(20)) #gfb
dragon_lord_hatchling.regTargetSpell("Light Heaing", 25, 55, check=chance(18))
#shoot fireball too?