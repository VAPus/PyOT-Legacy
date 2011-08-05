import game.monster

Stampor = game.monster.genMonster("Stampor", (381, 13246), "a Stampor")
Stampor.setTargetChance(10)
Stampor.bloodType("blood")
Stampor.setHealth(1200)
Stampor.setExperience(780)
Stampor.setSpeed(200) #incorrect
Stampor.walkAround(1,1,1) # energy, fire, poison
Stampor.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Stampor.voices("KRRRRRNG")
Stampor.setImmunity(1,1,0) # paralyze, invisible, lifedrain
Stampor.setDefense(3, fire=0.8, earth=1.0, energy=0.8, ice=0.9, holy=0.5, death=0.9, physical=1.0, drown=1.0) # not full correct
