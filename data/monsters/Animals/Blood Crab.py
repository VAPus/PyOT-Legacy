import game.monster

blood_crab = game.monster.genMonster("blood crab", (200, 6075), "a blood crab")
blood_crab.bloodType("blood")
blood_crab.setHealth(290)
blood_crab.setExperience(160)
blood_crab.setTargetChance(10)
blood_crab.setSpeed(200) # speed incorrect
blooc_crab.walkAround(1,1,0) # energy, fire, poison
blood_crab.setBehavior(summonable=505, attackable=1, hostile=1, illusionable=505, convinceable=505, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
blood_crab.setImmunity(0,0,0) # paralyze, invisible, lifedrain
blood_crab.setDefense(30, fire=1.1, earth=0, energy=1.05, ice=0, holy=1.0, death=1.0, physical=0.5, drown=0)
