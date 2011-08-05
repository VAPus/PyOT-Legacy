import game.monster

Skunk = game.monster.genMonster("Skunk", (106, 6035), "a Skunk")
Skunk.setTargetChance(0)
Skunk.bloodType("blood")
Skunk.setHealth(20)
Skunk.setExperience(3)
Skunk.setSpeed(136) #correct
Skunk.walkAround(1,1,1) # energy, fire, poison
Skunk.setBehavior(summonable=200, attackable=1, hostile=1, illusionable=200, convinceable=200, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=2)
Skunk.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Skunk.setDefense(3, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
