massive_fire_elemental = genMonster("Massive Fire Elemental", (242, 8964), "a massive fire elemental")
massive_fire_elemental.setHealth(1200, healthmax=1200)
massive_fire_elemental.bloodType("blood")
massive_fire_elemental.setDefense(armor=48, fire=0, earth=1, energy=0.7, ice=1.15, holy=1, death=0.8, physical=0.6, drown=1)
massive_fire_elemental.setExperience(950)
massive_fire_elemental.setSpeed(260)
massive_fire_elemental.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
massive_fire_elemental.walkAround(energy=1, fire=0, poison=1)
massive_fire_elemental.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
massive_fire_elemental.regMelee(100)