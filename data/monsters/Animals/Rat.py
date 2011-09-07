import game.monster

Rat = game.monster.genMonster("Rat", (21, 5964), "a rat")
Rat.setTargetChance(10)
Rat.bloodType("blood")
Rat.setHealth(20)
Rat.setExperience(5)
Rat.setSpeed(134) #correct
Rat.walkAround(1,1,1) # energy, fire, poison
Rat.setBehavior(summonable=220, hostile=1, illusionable=1, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=5)
Rat.voices("Meep!")
Rat.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Rat.setDefense(2, fire=1.0, earth=0.75, energy=1.0, ice=1.1, holy=0.9, death=1.1, physical=1.0, drown=1.0)
Rat.loot( ('cheese', 40), ('worm', 10.5, 3), ('gold coin', 43.75, 4) )