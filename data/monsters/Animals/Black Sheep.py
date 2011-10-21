black_sheep = game.monster.genMonster("black sheep", (13, 5994), "a black sheep")
black_sheep.bloodType("blood")
black_sheep.setHealth(20)
black_sheep.setExperience(0)
black_sheep.setTargetChance(10)
black_sheep.setSpeed(200) # speed incorrect
black_sheep.walkAround(1,1,1) # energy, fire, poison
black_sheep.setBehavior(summonable=250, hostile=0, illusionable=1, convinceable=250, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=20)
black_sheep.voices("Maeh")
black_sheep.setImmunity(0,0,0) # paralyze, invisible, lifedrain
black_sheep.setDefense(2, fire=1.1, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
black_sheep.loot( ('meat', 70.0, 5), ('black wool', 1.5) )