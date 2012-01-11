Barbarian_Headsplitter = game.monster.genMonster("Barbarian Headsplitter", (253, 6080), "a Barbarian Headsplitter")
Barbarian_Headsplitter.setOutfit(115,105,119,132)
Barbarian_Headsplitter.setTargetChance(10)
Barbarian_Headsplitter.bloodType("blood")
Barbarian_Headsplitter.setHealth(100)
Barbarian_Headsplitter.setExperience(85)
Barbarian_Headsplitter.setSpeed(168) # correct
Barbarian_Headsplitter.walkAround(1,1,1) # energy, fire, poison
Barbarian_Headsplitter.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=450, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Barbarian_Headsplitter.voices("I will regain my honor with your blood!", "Surrender is not an option!", "It's you or me!", "Die! Die! Die!")
Barbarian_Headsplitter.setImmunity(1,0,0) # paralyze, invisible, lifedrain
Barbarian_Headsplitter.setDefense(7, fire=1.0, earth=1.1, energy=0.8, ice=0.5, holy=0.8, death=1.1, physical=1.0, drown=1.0)
Barbarian_Headsplitter.regMelee(50)
Barbarian_Headsplitter.loot( (2148, 100, 30), ("torch", 60.5), ("brass helmet", 20.25), ("scale armor", 4.25), ("viking helmet", 4.5), ("knife", 15.0), ("health potion", 0.5), ("life ring", 0.25), ("skull", 3.25), ("krimhorn helmet", 0.0025), ("brown piece of cloth", 1.0, 3), ("fur boots", 0.0025) )