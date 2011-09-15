
Merlkin = game.monster.genMonster("Merlkin", (117, 6044), "a Merlkin")
Merlkin.setTargetChance(10)
Merlkin.bloodType("blood")
Merlkin.setHealth(235)
Merlkin.setExperience(145)
Merlkin.setSpeed(194)
Merlkin.walkAround(1,1,1) # energy, fire, poison
Merlkin.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=4, runOnHealth=0)
Merlkin.voices("Ugh! Ugh! Ugh!", "Holy banana!", "Chakka! Chakka!")
Merlkin.setImmunity(0,1,0) # paralyze, invisible, lifedrain
Merlkin.setDefense(18, fire=0.8, earth=1.0, energy=0.9, ice=1.15, holy=0.9, death=1.05, physical=1.0, drown=1.0)