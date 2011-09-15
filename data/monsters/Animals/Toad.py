Toad = game.monster.genMonster("Toad", (222, 6077), "a toad")
Toad.setTargetChance(10)
Toad.bloodType("blood")
Toad.setHealth(135)
Toad.setExperience(60)
Toad.setSpeed(210) #correct
Toad.walkAround(1,1,1) # energy, fire, poison
Toad.setBehavior(summonable=400, hostile=1, illusionable=1, convinceable=400, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=10)
Toad.voices("Ribbit!", "Ribbit! Ribbit!")
Toad.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Toad.setDefense(7, fire=1.1, earth=0.8, energy=1.0, ice=0.8, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Toad.loot( ('club', 2.25), ('fish', 19), ('mace', 3.75), ('gold coin', 24.5, 20), ('war hammer', 1.6), ('poisonous slime', 4.5) )