cave_rat = game.monster.genMonster("Cave Rat", (56, 5964), "a cave rat")
cave_rat.bloodType("blood")
cave_rat.setHealth(30)
cave_rat.setExperience(10)
cave_rat.setTargetChance(10)
cave_rat.setSpeed(150) # Correct
cave_rat.walkAround(1,1,1) # energy, fire, poison
cave_rat.setBehavior(summonable=250, hostile=1, illusionable=1, convinceable=250, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=3)
cave_rat.voices("Meep!", "Meeeeep!")
cave_rat.setImmunity(0,0,0) # paralyze, invisible, lifedrain
cave_rat.setDefense(2, fire=1.1, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
cave_rat.loot( ("cheese", 29.75), (2148, 100, 2), (3976, 15.0, 2), ("cookie", 1.0) )
cave_rat.regMelee(10)