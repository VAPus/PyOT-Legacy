Penguin = game.monster.genMonster("Penguin", (250, 7334), "a penguin")
Penguin.setTargetChance(0)
Penguin.bloodType("blood")
Penguin.setHealth(33)
Penguin.setExperience(1)
Penguin.setSpeed(200) #incorrect
Penguin.walkAround(1,1,1) # energy, fire, poison
Penguin.setBehavior(summonable=290, hostile=1, illusionable=1, convinceable=290, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=32)
Penguin.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Penguin.setDefense(2, fire=1.0, earth=1.0, energy=1.1, ice=0.8, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Penguin.loot( ('green perch', 0.6), ('rainbow trout', 0.6), ('fish', 5.5) )
Penguin.regMelee(3)