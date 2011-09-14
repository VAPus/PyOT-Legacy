import game.monster

Gazer = game.monster.genMonster("Gazer", (226, 6079), "a Gazer")
Gazer.setTargetChance(10)
Gazer.bloodType("blood")
Gazer.setHealth(120)
Gazer.setExperience(90)
Gazer.setSpeed(200) # not correct
Gazer.walkAround(1,1,0) # energy, fire, poison
Gazer.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=4, runOnHealth=0)
Gazer.voices("Mommy!?", "Buuuuhaaaahhaaaaa!", "We need mana!")
Gazer.setImmunity(0,1,0) # paralyze, invisible, lifedrain
Gazer.setDefense(4, fire=0.4, earth=0, energy=0.9, ice=0.8, holy=1.0, death=1.0, physical=1.0, drown=1.0)