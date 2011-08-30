import game.monster

bug = game.monster.genMonster("Bug", (45, 5990), "a bug")
bug.bloodType("slime")
bug.setHealth(29)
bug.setExperience(18)
bug.setTargetChance(10)
bug.setSpeed(160) #correct
bug.walkAround(1,1,1) # energy, fire, poison
bug.setBehavior(summonable=250, attackable=1, hostile=1, illusionable=1, convinceable=250, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
bug.setImmunity(0,0,0) # paralyze, invisible, lifedrain
bug.setDefense(2, fire=1.1, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
bug.loot( ('cherry', 2, 3), ('gold coin', 20, 6 ) )