
bat = game.monster.genMonster("Bat", (122, 6053), "a bat")
bat.bloodType("blood")
bat.setHealth(30)
bat.setExperience(10)
bat.setTargetChance(10)
bat.setSpeed(200) # speed correct
bat.walkAround(1,1,1) # energy, fire, poison
bat.setBehavior(summonable=250, hostile=1, illusionable=1, convinceable=205, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=3)
bat.voices("Flap! Flap!")
bat.setImmunity(0,0,0) # paralyze, invisible, lifedrain
bat.setDefense(2, fire=1.0, earth=1.05, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
bat.loot( ('bat wing', 1.5, 3 ) )