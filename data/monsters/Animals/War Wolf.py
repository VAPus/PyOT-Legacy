import game.monster
<-- War_Wolf -->
War_Wolf = game.monster.genMonster("War Wolf", (3, 6009), "a War Wolf")
War_Wolf.setTargetChance(10)
War_Wolf.bloodType("blood")
War_Wolf.setHealth(140)
War_Wolf.setExperience(55)
War_Wolf.setSpeed(264) #correct
War_Wolf.walkAround(1,1,1) # energy, fire, poison
War_Wolf.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=420, convinceable=420, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
War_Wolf.voices("Yoooohhuuuu!", "Grrrrrrrr")
War_Wolf.setImmunity(0,0,0) # paralyze, invisible, lifedrain
War_Wolf.setDefense(10, fire=1.0, earth=0.8, energy=1.0, ice=1.1, holy=0.9, death=1.08, physical=10, drown=1.0)
