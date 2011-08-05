import game.monster

Lion = game.monster.genMonster("Lion", (41, 5986), "a Lion")
Lion.setTargetChance(10)
Lion.bloodType("blood")
Lion.setHealth(80)
Lion.setExperience(30)
Lion.setSpeed(190) #correct
Lion.walkAround(1,1,1) # energy, fire, poison
Lion.setBehavior(summonable=320, attackable=1, hostile=1, illusionable=320, convinceable=320, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=10)
Lion.voices("Groarrr!")
Lion.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Lion.setDefense(10, fire=1.0, earth=0.8, energy=1.0, ice=1.15, holy=0.8, death=1.08, physical=1.0, drown=1.0)

