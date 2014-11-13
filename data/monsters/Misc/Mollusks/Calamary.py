Calamary = genMonster("Calamary", (8, 5980), "a calamary")
Calamary.health(75)
Calamary.type("blood") #?
Calamary.defense(armor=10, fire=0, earth=0, energy=0, ice=1, holy=1, death=1, physical=1, drown=0)
Calamary.experience(0)
Calamary.speed(350) #incorrect
Calamary.behavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0) #hostile?
Calamary.walkAround(energy=1, fire=0, poison=0)
Calamary.immunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
Calamary.voices("Bubble", "Bobble")