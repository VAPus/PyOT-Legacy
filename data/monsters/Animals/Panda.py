Panda = game.monster.genMonster("Panda", (123, 6049), "a panda")
Panda.setTargetChance(10)
Panda.bloodType("blood")
Panda.setHealth(80)
Panda.setExperience(23)
Panda.setSpeed(200) #incorrect
Panda.walkAround(1,1,0) # energy, fire, poison
Panda.setBehavior(summonable=300, hostile=1, illusionable=1, convinceable=300, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=10)
Panda.voices("Groar", "Grrrrr")
Panda.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Panda.setDefense(9, fire=1.1, earth=0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Panda.loot( ('ham', 34.5, 2), ('meat', 72.0, 4), ('bamboo stick', 3.25) )
Panda.regMelee(16)