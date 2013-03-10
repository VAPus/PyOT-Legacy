hive_pore = genMonster("Hive Pore", (0, 5980), "a hive pore") #is the name visable? incorrect look no corpse?
hive_pore.setHealth(1, healthmax=1)
hive_pore.bloodType("slime")
hive_pore.setDefense(armor=10, fire=0, earth=0, energy=0, ice=0, holy=0, death=0, physical=0, drown=0)
hive_pore.setExperience(0)
hive_pore.setSpeed(0) #doesnt move
hive_pore.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
hive_pore.walkAround(energy=0, fire=0, poison=0)
hive_pore.setImmunity(paralyze=0, invisible=1, lifedrain=0, drunk=0)
hive_pore.summon("Lesser Swarmer", 25)
hive_pore.maxSummons(3)