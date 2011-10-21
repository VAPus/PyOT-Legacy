Pig = game.monster.genMonster("Pig", (60, 6000), "a pig")
Pig.setTargetChance(0)
Pig.bloodType("blood")
Pig.setHealth(25)
Pig.setExperience(0)
Pig.setSpeed(200) #incorrect
Pig.walkAround(1,1,1) # energy, fire, poison
Pig.setBehavior(summonable=255, hostile=0, illusionable=1, convinceable=255, pushable=1, pushItems=0, pushCreatures=0, targetDistance=0, runOnHealth=25)
Pig.voices("Oink oink", "Oink")
Pig.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Pig.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Pig.loot( ('meat', 65.75, 4), ('pig foot', 1.25) )