Badger = genMonster("Badger", (105, 6034), "a badger")
Badger.type("blood")
Badger.health(23)
Badger.experience(5)
Badger.setTargetChance(10)
Badger.speed(200) # speed incorrect
Badger.walkAround(1,1,1) # energy, fire, poison
Badger.behavior(summonable=200, hostile=1, illusionable=1, convinceable=200, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=5)
Badger.immunity(0,0,0) # paralyze, invisible, lifedrain
Badger.defense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Badger.loot( ("beetroot", 40.5), ("badger fur", 10.75), ("acorn", 4.5) )
Badger.regMelee(12)