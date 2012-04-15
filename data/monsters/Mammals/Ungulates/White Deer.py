# bad  (suppose to summon enraged or hurt white deer when it dies)
White_Deer = game.monster.genMonster("White Deer", (400, 6079), "a white deer") # uknown yet
White_Deer.setTargetChance(10)
White_Deer.bloodType("blood")
White_Deer.setHealth(195)
White_Deer.setExperience(0)
White_Deer.setSpeed(220)
White_Deer.walkAround(1,1,1) # energy, fire, poison
White_Deer.setBehavior(summonable=0, hostile=0, illusionable=1, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=195)
White_Deer.voices("wheeze", "ROOOAAARR!!", "sniff", "bell")
White_Deer.setImmunity(0,0,0) # paralyze, invisible, lifedrain
White_Deer.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)