Penguin = genMonster("Penguin", (250, 7334), "a penguin")
Penguin.setTargetChance(0)
Penguin.type("blood")
Penguin.health(33)
Penguin.experience(1)
Penguin.speed(200) #incorrect
Penguin.walkAround(1,1,1) # energy, fire, poison
Penguin.behavior(summonable=290, hostile=1, illusionable=1, convinceable=290, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=32)
Penguin.immunity(0,0,0) # paralyze, invisible, lifedrain
Penguin.defense(2, fire=1.0, earth=1.0, energy=1.1, ice=0.8, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Penguin.loot( ("fish", 11.0, 2), ("rainbow trout", 0.0025), ("green perch", 0.25) )
Penguin.regMelee(3)