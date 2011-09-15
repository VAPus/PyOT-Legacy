
Valkyrie = game.monster.genMonster("Valkyrie", (139, 6080), "a Valkyrie")
Valkyrie.setOutfit(113, 57, 95, 113)
Valkyrie.setTargetChance(10)
Valkyrie.bloodType("blood")
Valkyrie.setHealth(190)
Valkyrie.setExperience(85)
Valkyrie.setSpeed(176) # Correct
Valkyrie.walkAround(1,1,1) # energy, fire, poison
Valkyrie.setBehavior(summonable=450, hostile=1, illusionable=450, convinceable=450, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=10)
Valkyrie.voices("Another head for me!", "Head off!", "Your hea will be mine!", "Stand still!", "One more head for me!")
Valkyrie.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Valkyrie.setDefense(13, fire=0.9, earth=1.0, energy=1.0, ice=0.9, holy=0.95, death=1.05, physical=1.1, drown=1.0)