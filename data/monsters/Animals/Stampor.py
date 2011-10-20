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
Stampor.loot( ('gold coin', 26.25, 244), ('strong health potion', 8), ('knight armor', 1.25), ('war hammer', 1.5), ('small topaz', 6.5, 2), ('strong mana potion', 4, 2), ('platinum coin', 7.75, 2), ('spiked squelcher', 0.525) ) # , ('stampor talon', 11), ('stampor horn', 5.5), ('hollow stampor hoof', 3.5)
Stampor.regMelee(130)