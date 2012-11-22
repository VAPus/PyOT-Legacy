#some incorrect information
midnight_spawn = genMonster("Midnight Spawn", (315, 9960), "a midnight spawn")
midnight_spawn.setHealth(320)
midnight_spawn.bloodType("undead")
midnight_spawn.setDefense(armor=44, fire=0.7, earth=0.01, energy=1, ice=1.1, holy=1.1, death=0.01, physical=0.7, drown=1)
midnight_spawn.setExperience(300)
midnight_spawn.setSpeed(230)
midnight_spawn.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
midnight_spawn.walkAround(energy=1, fire=1, poison=0)
midnight_spawn.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)#.99% immune to life drain?
midnight_spawn.regMelee(150)
midnight_spawn.loot( ("midnight shard", 13.5) )