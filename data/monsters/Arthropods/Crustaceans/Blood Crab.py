blood_crab = genMonster("Blood Crab", (200, 6075), "a blood crab")
blood_crab.type("blood")
blood_crab.health(290)
blood_crab.experience(160)
blood_crab.setTargetChance(10)
blood_crab.speed(200) # speed incorrect
blood_crab.walkAround(1,1,0) # energy, fire, poison
blood_crab.behavior(summonable=505, hostile=1, illusionable=1, convinceable=505, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
blood_crab.immunity(0,0,0) # paralyze, invisible, lifedrain
blood_crab.defense(31, fire=1.1, earth=0, energy=1.05, ice=0, holy=1.0, death=1.0, physical=0.5, drown=0)
blood_crab.loot( ("chain armor", 5.0), ("brass legs", 1.75), (10550, 7.0), (2148, 100, 20), ("fish", 11.25), ("white pearl", 0.5) )

blood_crab.regMelee(110)