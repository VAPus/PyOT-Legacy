Hunter = game.monster.genMonster("Hunter", (129, 6080), "a Hunter")
Hunter.setOutfit(95, 116, 121, 115)
Hunter.setTargetChance(10)
Hunter.bloodType("blood")
Hunter.setHealth(150)
Hunter.setExperience(150)
Hunter.setSpeed(210) # Correct
Hunter.walkAround(1,1,1) # energy, fire, poison
Hunter.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=530, pushable=0, pushItems=1, pushCreatures=0, targetDistance=4, runOnHealth=15)
Hunter.voices("Guess who we are hunting!", "Guess who we're hunting, hahaha!", "Bullseye!", "You'll make a nice trophy!")
Hunter.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Hunter.setDefense(9, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=0.8, death=1.0, physical=1.05, drown=1.0)
Hunter.regMelee(20)