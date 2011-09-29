Crazed_Beggar = game.monster.genMonster("Crazed Beggar", (153, 6080), "a Crazed Beggar")
Crazed_Beggar.setOutfit(38, 97, 59, 38)
Crazed_Beggar.setAddons(3)
Crazed_Beggar.setTargetChance(0)
Crazed_Beggar.bloodType("blood")
Crazed_Beggar.setHealth(100)
Crazed_Beggar.setExperience(35)
Crazed_Beggar.setSpeed(134) # Correct
Crazed_Beggar.walkAround(1,1,1) # energy, fire, poison
Crazed_Beggar.setBehavior(summonable=300, hostile=1, illusionable=0, convinceable=300, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Crazed_Beggar.voices("Hehehe!", "Raahhh!", "You are one of THEM! Die!", "Wanna buy roses??", "Make it stop!")
Crazed_Beggar.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Crazed_Beggar.setDefense(4, fire=1.0, earth=1.1, energy=0.8, ice=1.0, holy=0.9, death=1.1, physical=0.9, drown=1.0)
Crazed_Beggar.regMelee(25)