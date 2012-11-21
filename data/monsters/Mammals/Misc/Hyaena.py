Hyaena = genMonster("Hyaena", (94, 6026), "a hyaena")
Hyaena.setTargetChance(10)
Hyaena.bloodType("blood")
Hyaena.setHealth(60)
Hyaena.setExperience(20)
Hyaena.setSpeed(196) #correct
Hyaena.walkAround(1,1,1) # energy, fire, poison
Hyaena.setBehavior(summonable=275, hostile=1, illusionable=1, convinceable=275, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=30)
Hyaena.voices("Grrrrrr", "Hou hou hou!")
Hyaena.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Hyaena.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Hyaena.loot( (3976, 100, 3), ("meat", 39.25, 2) )
Hyaena.regMelee(20)