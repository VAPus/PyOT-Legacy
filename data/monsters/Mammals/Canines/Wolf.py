Wolf = genMonster("Wolf", (27, 5968), "a wolf")
Wolf.setTargetChance(0)
Wolf.bloodType("blood")
Wolf.setHealth(25)
Wolf.setExperience(18)
Wolf.setSpeed(164) #correct
Wolf.walkAround(1,1,1) # energy, fire, poison
Wolf.setBehavior(summonable=255, hostile=1, illusionable=1, convinceable=255, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=8)
Wolf.voices("Yooooohhuuuu!", "Grrrrrrrr")
Wolf.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Wolf.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.1, holy=0.9, death=1.05, physical=1.0, drown=1.0)
Wolf.loot( ("meat", 67.5), ("wolf paw", 1.0, 3) )
Wolf.regMelee(19)