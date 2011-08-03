import game.monster
<-- Deer -->
Deer = game.monster.genMonster("Deer", (31, 5970), "a Deer")
Deer.setTargetChance(10)
Deer.bloodType("blood")
Deer.setHealth(25)
Deer.setExperience(0)
Deer.setSpeed(196) # correct
Deer.walkAround(1,1,1) # energy, fire, poison
Deer.setBehavior(summonable=260, attackable=1, hostile=0, illusionable=260, convinceable=260, pushable=1, pushItems=0, pushCreatures=0, runOnHealth=25)
Deer.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Deer.setDefense(3, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
