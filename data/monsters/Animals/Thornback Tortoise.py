import game.monster

Thornback_Tortoise = game.monster.genMonster("Thornback Tortoise", (198, 6073), "a Thornback Tortoise")
Thornback_Tortoise.setTargetChance(10)
Thornback_Tortoise.bloodType("blood")
Thornback_Tortoise.setHealth(300)
Thornback_Tortoise.setExperience(150)
Thornback_Tortoise.setSpeed(200) #incorrect
Thornback_Tortoise.walkAround(1,1,1) # energy, fire, poison
Thornback_Tortoise.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=490, convinceable=490, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Thornback_Tortoise.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Thornback_Tortoise.setDefense(30, fire=1.1, earth=0.8, energy=1.0, ice=0.8, holy=1.0, death=1.0, physical=0.7, drown=1.0)
