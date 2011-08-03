import game.monster
<-- Werewolf -->
Werewolf = game.monster.genMonster("Werewolf", (308, 6080), "a Werewolf")
Werewolf.setTargetChance(10)
Werewolf.bloodType("blood")
Werewolf.setHealth(1955)
Werewolf.setExperience(1900)
Werewolf.setSpeed(200) #incorrect
Werewolf.walkAround(0,1,0) # energy, fire, poison
Werewolf.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=195)
Werewolf.voices("BLOOD!", "HRAAAAAAAARRRRRR!")
Werewolf.setImmunity(1,1,1) # paralyze, invisible, lifedrain
Werewolf.setDefense(40, fire=1.05, earth=0.75, energy=0.85, ice=1.1, holy=1.05, death=0.45, physical=1.0, drown=1.0)
