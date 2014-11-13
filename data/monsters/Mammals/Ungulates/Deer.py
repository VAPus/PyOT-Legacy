Deer = genMonster("Deer", (31, 5970), "a deer")
Deer.setTargetChance(10)
Deer.type("blood")
Deer.health(25)
Deer.experience(0)
Deer.speed(196) # correct
Deer.walkAround(1,1,1) # energy, fire, poison
Deer.behavior(summonable=260, hostile=0, illusionable=1, convinceable=260, pushable=1, pushItems=0, pushCreatures=0, runOnHealth=25)
Deer.immunity(0,0,0) # paralyze, invisible, lifedrain
Deer.defense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Deer.loot( ("ham", 49.25, 2), ("meat", 79.5, 4), ("antlers", 1.0) )
Deer.regMelee(1)#when a summon? probably incorrect information