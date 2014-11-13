Skunk = genMonster("Skunk", (106, 6035), "a skunk")
Skunk.setTargetChance(0)
Skunk.type("blood")
Skunk.health(20)
Skunk.experience(3)
Skunk.speed(136) #correct
Skunk.walkAround(1,1,1) # energy, fire, poison
Skunk.behavior(summonable=200, hostile=1, illusionable=1, convinceable=200, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=2)
Skunk.immunity(0,0,0) # paralyze, invisible, lifedrain
Skunk.defense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Skunk.loot( ("bulb of garlic", 4.75), ("skunk tail", 1.25) ) #it drops worms too
Skunk.regMelee(5)