#mostly unknown
clay_guardian = game.monster.genMonster("Clay Guardian", (8, 5980), "a clay guardian")
clay_guardian.setHealth(625)
clay_guardian.bloodType(color="blood")
clay_guardian.setDefense(armor=46, fire=1, earth=0, energy=0.7, ice=0.65, holy=1, death=0.6, physical=0.75, drown=1)
clay_guardian.setExperience(400)
clay_guardian.setSpeed(250)
clay_guardian.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
clay_guardian.walkAround(energy=0, fire=0, poison=0)
clay_guardian.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
#clay_guardian.voices(*arg)
clay_guardian.regMelee(120)
clay_guardian.loot( (2148, 100, 158), ("small stone", 60.75, 10), ("lump of earth", 27.0), ("blank rune", 25.25), ("earth arrow", 21.0, 8), ("clay lump", 1.25), ("small topaz", 0.0025) )