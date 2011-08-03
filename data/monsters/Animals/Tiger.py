import game.monster
<-- Tiger -->
Tiger = game.monster.genMonster("Tiger", (125, 051), "a Tiger")
Tiger.setTargetChance(10)
Tiger.bloodType("blood")
Tiger.setHealth(75)
Tiger.setExperience(40)
Tiger.setSpeed(200) #correct
Tiger.walkAround(1,1,1) # energy, fire, poison
Tiger.setBehavior(summonable=420, attackable=1, hostile=1, illusionable=420, convinceable=420, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Tiger.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Tiger.setDefense(5, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.0, drown=1.0)
