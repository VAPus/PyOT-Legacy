Deer = genMonster("Deer", (31, 5970), "a deer")
Deer.setTargetChance(10)
Deer.bloodType("blood")
Deer.setHealth(25)
Deer.setExperience(0)
Deer.setSpeed(196) # correct
Deer.walkAround(1,1,1) # energy, fire, poison
Deer.setBehavior(summonable=260, hostile=0, illusionable=1, convinceable=260, pushable=1, pushItems=0, pushCreatures=0, runOnHealth=25)
Deer.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Deer.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Deer.loot( ("ham", 49.25, 2), ("meat", 79.5, 4), ("antlers", 1.0) )
Deer.regMelee(1)#when a summon? probably incorrect information