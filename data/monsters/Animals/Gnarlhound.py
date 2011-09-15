
Gnarlhound = game.monster.genMonster("Gnarlhound", (341, 11250), "a gnarlhound")
Gnarlhound.setTargetChance(10)
Gnarlhound.bloodType("blood")
Gnarlhound.setHealth(198)
Gnarlhound.setExperience(60)
Gnarlhound.setSpeed(200) # incorrect
Gnarlhound.walkAround(1,1,1) # energy, fire, poison
Gnarlhound.setBehavior(summonable=465, hostile=1, illusionable=1, convinceable=465, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=20)
Gnarlhound.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Gnarlhound.setDefense(12, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Gnarlhound.loot( ('worm', 32.25, 3), ('shaggy tail', 20), ('meat', 12.5, 3) )