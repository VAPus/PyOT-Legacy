Barbarian_Skullhunter = genMonster("Barbarian Skullhunter", (254, 6080), "a Barbarian Skullhunter")
Barbarian_Skullhunter.setOutfit(0,77,77,114)
Barbarian_Skullhunter.setTargetChance(10)
Barbarian_Skullhunter.bloodType("blood")
Barbarian_Skullhunter.setHealth(135)
Barbarian_Skullhunter.setExperience(85)
Barbarian_Skullhunter.setSpeed(188) # Correct
Barbarian_Skullhunter.walkAround(1,1,1) # energy, fire, poison
Barbarian_Skullhunter.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=450, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Barbarian_Skullhunter.voices("You will become my trophy", "Fight harder, coward", "Show that you are a worthy opponent")
Barbarian_Skullhunter.setImmunity(1,0,0) # paralyze, invisible, lifedrain
Barbarian_Skullhunter.setDefense(9, fire=1.0, earth=1.1, energy=0.8, ice=0.5, holy=0.9, death=1.05, physical=0.9, drown=1.0)
Barbarian_Skullhunter.regMelee(65)
Barbarian_Skullhunter.loot( (3031, 100, 30), ("knife", 14.75), ("brass helmet", 20.75), ("torch", 60.0), ("skull", 3.0), ("viking helmet", 8.0), ("scale armor", 3.75), ("health potion", 0.75), ("crystal sword", 0.25), ("brown piece of cloth", 0.5, 3), ("ragnir helmet", 0.0025), ("life ring", 0.25), ("fur boots", 0.0025) )