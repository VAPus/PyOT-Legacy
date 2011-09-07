import game.monster

Orchid_Frog = game.monster.genMonster("Orchid Frog", (226, 6079), "an orchid frog")
Orchid_Frog.setOutfit(109, 14, 109, 114)
Orchid_Frog.setTargetChance(10)
Orchid_Frog.bloodType("blood")
Orchid_Frog.setHealth(60)
Orchid_Frog.setExperience(20)
Orchid_Frog.setSpeed(200) # incorrect
Orchid_Frog.walkAround(1,1,1) # energy, fire, poison
Orchid_Frog.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Orchid_Frog.voices("Ribbit!", "Ribbit! Ribbit!")
Orchid_Frog.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Orchid_Frog.setDefense(9, fire=1.1, earth=1.0, energy=1.0, ice=0.85, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Orchid_Frog.loot( ('worm', 9), ('gold coin', 30.5, 10) )
