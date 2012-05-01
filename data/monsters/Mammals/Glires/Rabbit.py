Rabbit = genMonster("Rabbit", (74, 6017), "a rabbit")
Rabbit.setTargetChance(0)
Rabbit.bloodType("blood")
Rabbit.setHealth(15)
Rabbit.setExperience(0)
Rabbit.setSpeed(180) #correct
Rabbit.walkAround(1,1,1) # energy, fire, poison
Rabbit.setBehavior(summonable=220, hostile=0, illusionable=1, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=0, runOnHealth=15)
Rabbit.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Rabbit.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Rabbit.loot( ("meat", 86.5, 2), ("carrot", 9.25) )