import game.monster

Polar_Bear = game.monster.genMonster("Polar Bear", (42, 5987), "a polar bear")
Polar_Bear.setTargetChance(10)
Polar_Bear.bloodType("blood")
Polar_Bear.setHealth(85)
Polar_Bear.setExperience(28)
Polar_Bear.setSpeed(156) #correct
Polar_Bear.walkAround(1,1,1) # energy, fire, poison
Polar_Bear.setBehavior(summonable=315, attackable=1, hostile=1, illusionable=315, convinceable=315, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=5)
Polar_Bear.voices("GROARRR!")
Polar_Bear.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Polar_Bear.setDefense(10, fire=0.9, earth=1.0, energy=1.05, ice=0.8, holy=1.0, death=1.1, physical=1.0, drown=1.0)
