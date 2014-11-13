Gazer = genMonster("Gazer", (226, 6079), "a Gazer")
Gazer.setTargetChance(10)
Gazer.type("blood")
Gazer.health(120)
Gazer.experience(90)
Gazer.speed(200) # not correct
Gazer.walkAround(1,1,0) # energy, fire, poison
Gazer.behavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=4, runOnHealth=0)
Gazer.voices("Mommy!?", "Buuuuhaaaahhaaaaa!", "We need mana!")
Gazer.immunity(0,1,0) # paralyze, invisible, lifedrain
Gazer.defense(4, fire=0.4, earth=0, energy=0.9, ice=0.8, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Gazer.regMelee(20)#ish~