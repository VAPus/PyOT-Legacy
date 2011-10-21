Dark_Monk = game.monster.genMonster("Dark Monk", (225, 6080), "a Dark Monk")
Dark_Monk.setTargetChance(10)
Dark_Monk.bloodType("blood")
Dark_Monk.setHealth(190)
Dark_Monk.setExperience(145)
Dark_Monk.setSpeed(230) # Correct
Dark_Monk.walkAround(1,1,1) # energy, fire, poison
Dark_Monk.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=480, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Dark_Monk.voices("You are no match to us!", "Your end has come!", "This is where your path will end!")
Dark_Monk.setImmunity(0,1,0) # paralyze, invisible, lifedrain
Dark_Monk.setDefense(22, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=0.9, death=0.6, physical=1.05, drown=1.0)
Dark_Monk.regMelee(100)
Dark_Monk.loot( ('dark rosary', 11.25), ('sandals', 1.0), (2148, 100, 18), ('mana potion', 1.0), ('safety pin', 1.0), ('lamp', 0.25), ('rope belt', 7.5), ('bread', 22.25), ('life crystal', 1.25), ('book of prayers', 2.0), ('ankh', 1.25), ('scroll', 2.25), ('power ring', 0.0025) )