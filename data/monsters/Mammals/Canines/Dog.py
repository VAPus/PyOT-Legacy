Dog = genMonster("Dog", (32, 5971), "a dog")
Dog.setTargetChance(10)
Dog.type("blood")
Dog.health(20)
Dog.experience(0)
Dog.speed(124) # correct
Dog.walkAround(1,1,1) # energy, fire, poison
Dog.behavior(summonable=220, hostile=1, illusionable=1, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=8)
Dog.voices("Wuff Wuff")
Dog.immunity(0,0,0) # paralyze, invisible, lifedrain
Dog.defense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)