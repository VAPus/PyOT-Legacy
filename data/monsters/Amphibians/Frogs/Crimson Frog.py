crimson_frog = game.monster.genMonster("Crimson Frog", (226, 6079), "a crimson frog")
crimson_frog.setOutfit(94, 78, 94, 78)
crimson_frog.setTargetChance(10)
crimson_frog.bloodType("blood")
crimson_frog.setHealth(60)
crimson_frog.setExperience(20)
crimson_frog.setSpeed(200)
crimson_frog.walkAround(1,1,1) # energy, fire, poison
crimson_frog.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
crimson_frog.voices("Ribbit!", "Ribbit! Ribbit!")
crimson_frog.setImmunity(0,0,0) # paralyze, invisible, lifedrain
crimson_frog.setDefense(9, fire=1.1, earth=1.0, energy=1.0, ice=0.85, holy=1.0, death=1.0, physical=1.0, drown=1.0)
crimson_frog.loot( (2148, 100, 10), (3976, 9.0) )
crimson_frog.regMelee(24)