Stampor = game.monster.genMonster("Stampor", (381, 13246), "a stampor")
Stampor.setTargetChance(10)
Stampor.bloodType("blood")
Stampor.setHealth(1200)
Stampor.setExperience(780)
Stampor.setSpeed(200) #incorrect
Stampor.walkAround(1,1,1) # energy, fire, poison
Stampor.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Stampor.voices("KRRRRRNG")
Stampor.setImmunity(1,1,0) # paralyze, invisible, lifedrain
Stampor.setDefense(20, fire=0.8, earth=1.0, energy=0.8, ice=0.9, holy=0.5, death=0.9, physical=1.0, drown=1.0) # not full correct
Stampor.loot( ('spiked squelcher', 0.25), ('knight armor', 1.0), ('war hammer', 1.0), ('hollow stampor hoof', 2.75), ('stampor horn', 5.25), ('strong health potion', 7.0, 2), ('platinum coin', 15.0, 2), ('strong mana potion', 7.5, 2), ('small topaz', 12.25, 2), ('stampor talons', 10.75), (2148, 100, 244) ) # , ('stampor talon', 11), ('stampor horn', 5.5), ('hollow stampor hoof', 3.5)
Stampor.regMelee(130)