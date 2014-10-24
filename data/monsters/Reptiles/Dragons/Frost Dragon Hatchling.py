frost_dragon_hatchling = genMonster("Frost Dragon Hatchling", (283, 7969), "a frost dragon hatchling")
frost_dragon_hatchling.setHealth(800)
frost_dragon_hatchling.bloodType("undead")
frost_dragon_hatchling.setDefense(armor=35, fire=0, earth=0, energy=1.05, ice=0, holy=1, death=1, physical=1, drown=1)
frost_dragon_hatchling.setExperience(745)
frost_dragon_hatchling.setSpeed(170)
frost_dragon_hatchling.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=100)
frost_dragon_hatchling.walkAround(energy=1, fire=0, poison=0)
frost_dragon_hatchling.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
frost_dragon_hatchling.voices("Rooawwrr", "Fchu?")
frost_dragon_hatchling.loot( ("spellbook of enlightenment", 0.5), ("frosty heart", 5.0), ("dragon ham", 80.0), (2148, 100, 55), ("health potion", 0.5) )

fdhwave = spell.Spell("fdh iwave", target=TARGET_AREA)
fdhwave.area(AREA_WAVE42)
fdhwave.element(ICE)
fdhwave.effects(area=EFFECT_ICEATTACK)

frost_dragon_hatchling.regMelee(160)
frost_dragon_hatchling.regSelfSpell("Light Healing", 40, 60, check=chance(18))
frost_dragon_hatchling.regTargetSpell("fdh iwave", 60, 110, check=chance(20))
frost_dragon_hatchling.regTargetSpell(2274, 60, 110, check=chance(20)) #avalache
#Distance Paralyze missing