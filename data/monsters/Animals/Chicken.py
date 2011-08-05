import game.monster

chicken = game.monster.genMonster("chicken", (111, 6042), "a chicken")
chicken.bloodType("blood")
chicken.setHealth(15)
chicken.setExperience(0)
chicken.setTargetChance(10)
chicken.setSpeed(200) #Incorrect
chicken.walkAround(1,1,1) # energy, fire, poison
chicken.setBehavior(summonable=220, attackable=1, hostile=1, illusionable=220, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
chicken.voices("Cluck Cluck", "Gokgoooook")
chicken.setImmunity(0,0,0) # paralyze, invisible, lifedrain
chicken.setDefense(3, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
