Barbarian_Brutetamer = game.monster.genMonster("Barbarian Brutetamer", (264, 6081), "a Barbarian Brutetamer")
Barbarian_Brutetamer.setOutfit(78,116,95,121)
Barbarian_Brutetamer.setTargetChance(10)
Barbarian_Brutetamer.bloodType("blood")
Barbarian_Brutetamer.setHealth(145)
Barbarian_Brutetamer.setExperience(90)
Barbarian_Brutetamer.setSpeed(178) #correct
Barbarian_Brutetamer.walkAround(1,1,1) # energy, fire, poison
Barbarian_Brutetamer.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=4, runOnHealth=14)
Barbarian_Brutetamer.voices("To me, creatures of the wold!", "My instincts tell me about your cowardice.", "Feel the power of the beast!")
Barbarian_Brutetamer.setImmunity(1,1,1) # paralyze, invisible, lifedrain
Barbarian_Brutetamer.setDefense(9, fire=1.0, earth=0.8, energy=1.0, ice=0.5, holy=0.9, death=1.05, physical=1.1, drown=1.0)
Barbarian_Brutetamer.summon("War Wolf", 10)
Barbarian_Brutetamer.maxSummons(2)
Barbarian_Brutetamer.regMelee(20)