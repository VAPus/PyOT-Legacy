Rift_Worm = genMonster("Rift Worm", (295, 0), "a Rift Worm")
Rift_Worm.setTargetChance(10)
Rift_Worm.bloodType("blood")
Rift_Worm.setHealth(2800)
Rift_Worm.setExperience(1950)
Rift_Worm.setSpeed(136) # Correct
Rift_Worm.walkAround(1,1,1) # energy, fire, poison
Rift_Worm.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Rift_Worm.setImmunity(1,1,1) # paralyze, invisible, lifedrain
Rift_Worm.setDefense(31, fire=1.05, earth=0.7, energy=0.9, ice=1.05, holy=1.05, death=0.95, physical=1.05, drown=1.0)
Rift_Worm.regMelee(160)#ish?