import game.monster
# bad
Thornfire_Wolf = game.monster.genMonster("Thornfire Wolf", (414, 6079), "a thornfire wolf") # unkown yet
Thornfire_Wolf.setTargetChance(10)
Thornfire_Wolf.bloodType("blood")
Thornfire_Wolf.setHealth(600)
Thornfire_Wolf.setExperience(200)
Thornfire_Wolf.setSpeed(200) #incorrect
Thornfire_Wolf.walkAround(1,0,1) # energy, fire, poison
Thornfire_Wolf.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Thornfire_Wolf.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Thornfire_Wolf.setDefense(3, fire=0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0) 
