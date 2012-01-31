Sibang = game.monster.genMonster("Sibang", (118, 6045), "a Sibang")
Sibang.setTargetChance(10)
Sibang.bloodType("blood")
Sibang.setHealth(225)
Sibang.setExperience(105)
Sibang.setSpeed(214) # correct
Sibang.walkAround(1,1,1) # energy, fire, poison
Sibang.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=4, runOnHealth=0)
Sibang.voices("Eeeeek! Eeeeek!", "Huh! Huh! Huh!", "Ahhuuaaa!")
Sibang.setImmunity(0,1,0) # paralyze, invisible, lifedrain
Sibang.setDefense(11, fire=0.75, earth=1.0, energy=1.0, ice=1.15, holy=0.9, death=1.05, physical=1.0, drown=1.0)
Sibang.regMelee(40)
Sibang.regDistance(55, ANIMATION_SMALLSTONE, game.monster.chance(21))
Sibang.loot( ("orange", 61.5, 5), ("small stone", 61.5, 3), ("banana sash", 5.0), (2148, 100, 35), ("banana", 48.0, 11), ("ape fur", 1.25, 3), ("coconut", 3.75, 3), ("melon", 1.0) )