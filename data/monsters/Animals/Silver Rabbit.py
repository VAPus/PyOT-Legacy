import game.monster

Silver_Rabbit = game.monster.genMonster("Silver Rabbit", (252, 7338), "a silver rabbit")
Silver_Rabbit.setTargetChance(10)
Silver_Rabbit.bloodType("blood")
Silver_Rabbit.setHealth(15)
Silver_Rabbit.setExperience(0)
Silver_Rabbit.setSpeed(184) #correct
Silver_Rabbit.walkAround(1,1,1) # energy, fire, poison
Silver_Rabbit.setBehavior(summonable=220, attackable=1, hostile=0, illusionable=1, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=15)
Silver_Rabbit.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Silver_Rabbit.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Silver_Rabbit.loot( ('carrot', 9), ('meat', 42.5 ,2), ('silky fur', 26.5) )