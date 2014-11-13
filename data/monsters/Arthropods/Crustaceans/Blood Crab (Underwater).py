blood_crab = genMonster("Blood Crab", (200, 6075), "a blood crab")
blood_crab.type("blood")
blood_crab.health(320)
blood_crab.experience(180)
blood_crab.setTargetChance(10)
blood_crab.speed(200) # speed incorrect
blood_crab.walkAround(1,1,0) # energy, fire, poison
blood_crab.behavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
blood_crab.immunity(0,0,0) # paralyze, invisible, lifedrain
blood_crab.defense(31, fire=0, earth=0, energy=1.05, ice=0, holy=1.0, death=1.0, physical=0.99, drown=0)

blood_crab.regMelee(111)