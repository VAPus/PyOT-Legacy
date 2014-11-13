Mammoth = genMonster("Mammoth", (199, 6074), "a mammoth")
Mammoth.setTargetChance(10)
Mammoth.type("blood")
Mammoth.health(320)
Mammoth.experience(160)
Mammoth.speed(190) #correct
Mammoth.walkAround(1,1,1) # energy, fire, poison
Mammoth.behavior(summonable=0, hostile=1, illusionable=0, convinceable=500, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Mammoth.voices("Troooooot!", "Hooooot-Toooooot!", "Tooooot.")
Mammoth.immunity(0,0,0) # paralyze, invisible, lifedrain
Mammoth.defense(23, fire=1.1, earth=0.8, energy=1.0, ice=0.8, holy=1.0, death=1.0, physical=0.8, drown=1.0)
Mammoth.loot( ("ham", 27.0, 3), ("thick fur", 2.0), (2148, 100, 20), ("mammoth tusk", 8.25, 2), ("furry club", 0.5), ("meat", 26.75), ("tusk shield", 0.0025) )
Mammoth.regMelee(110)