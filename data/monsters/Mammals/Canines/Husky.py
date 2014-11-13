Husky = genMonster("Husky", (258, 7316), "a husky")
Husky.setTargetChance(10)
Husky.type("blood")
Husky.health(140)
Husky.experience(0)
Husky.speed(264) #correct
Husky.walkAround(1,1,1) # energy, fire, poison
Husky.behavior(summonable=420, hostile=1, illusionable=1, convinceable=420, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=100)
Husky.voices("Yoooohuuuu!", "Grrrrrrr", "Ruff, ruff!")
Husky.immunity(0,0,0) # paralyze, invisible, lifedrain
Husky.defense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)