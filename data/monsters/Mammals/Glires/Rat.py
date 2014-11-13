Rat = genMonster("Rat", (21, 5964), "a rat")
Rat.setTargetChance(10)
Rat.type("blood")
Rat.health(20)
Rat.experience(5)
Rat.speed(134) #correct
Rat.walkAround(1,1,1) # energy, fire, poison
Rat.behavior(summonable=220, hostile=1, illusionable=1, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=5)
Rat.voices("Meep!")
Rat.immunity(0,0,0) # paralyze, invisible, lifedrain
Rat.defense(2, fire=1.0, earth=0.75, energy=1.0, ice=1.1, holy=0.9, death=1.1, physical=1.0, drown=1.0)
Rat.loot( ("cheese", 39.25), (2148, 100, 4) )
Rat.regMelee(8)