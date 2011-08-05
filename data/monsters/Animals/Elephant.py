import game.monster

Elephant = game.monster.genMonster("Elephant", (211, 6052), "a Elephant")
Elephant.setTargetChance(10)
Elephant.bloodType("blood")
Elephant.setHealth(320)
Elephant.setExperience(160)
Elephant.setSpeed(190) # correct
Elephant.walkAround(1,1,1) # energy, fire, poison
Elephant.setBehavior(summonable=500, attackable=1, hostile=1, illusionable=500, convinceable=500, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Elephant.voices("Hooooot-Toooooot!", "Tooooot!", "Troooooot!")
Elephant.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Elephant.setDefense(20, fire=1.0, earth=1.0, energy=1.1, ice=0.8, holy=1.0, death=1.0, physical=0.9, drown=1.0)
