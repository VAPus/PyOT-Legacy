bug = genMonster("Bug", (45, 5990), "a bug")
bug.type("slime")
bug.health(29)
bug.experience(18)
bug.setTargetChance(10)
bug.speed(160) #correct
bug.walkAround(1,1,1) # energy, fire, poison
bug.behavior(summonable=250, hostile=1, illusionable=1, convinceable=250, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
bug.immunity(0,0,0) # paralyze, invisible, lifedrain
bug.defense(2, fire=1.1, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
bug.loot( ("cherry", 5.5, 3), (2148, 100, 6) )
bug.regMelee(23)