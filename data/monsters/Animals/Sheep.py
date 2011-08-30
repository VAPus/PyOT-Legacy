import game.monster

Sheep = game.monster.genMonster("Sheep", (14, 5991), "a sheep")
Sheep.setTargetChance(0)
Sheep.bloodType("blood")
Sheep.setHealth(20)
Sheep.setExperience(0)
Sheep.setSpeed(200) #incorrect
Sheep.walkAround(1,1,1) # energy, fire, poison
Sheep.setBehavior(summonable=250, attackable=1, hostile=0, illusionable=1, convinceable=250, pushable=1, pushItems=0, pushCreatures=0, targetDistance=0, runOnHealth=20)
Sheep.voices("Maeh")
Sheep.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Sheep.setDefense(2, fire=1.1, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Sheep.loot( ('meat', 17), ('wool', 2) )