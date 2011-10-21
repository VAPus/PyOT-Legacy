chicken = game.monster.genMonster("chicken", (111, 6042), "a chicken")
chicken.bloodType("blood")
chicken.setHealth(15)
chicken.setExperience(0)
chicken.setTargetChance(10)
chicken.setSpeed(200) #Incorrect
chicken.walkAround(1,1,1) # energy, fire, poison
chicken.setBehavior(summonable=220, hostile=1, illusionable=1, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
chicken.voices("Cluck Cluck", "Gokgoooook")
chicken.setImmunity(0,0,0) # paralyze, invisible, lifedrain
chicken.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
chicken.loot( ('chicken feather', 20.25, 3), (3976, 17.5, 3), ('meat', 2.25), ('egg', 1.25) )