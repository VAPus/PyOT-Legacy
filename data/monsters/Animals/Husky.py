import game.monster
<-- Husky -->
Husky = game.monster.genMonster("Husky", (258, 7316), "a Husky")
Husky.setTargetChance(10)
Husky.bloodType("blood")
Husky.setHealth(140)
Husky.setExperience(0)
Husky.setSpeed(264) #correct
Husky.walkAround(1,1,1) # energy, fire, poison
Husky.setBehavior(summonable=420, attackable=1, hostile=1, illusionable=420, convinceable=420, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=100)
Husky.voices("Yoooohuuuu!", "Grrrrrrr", "Ruff, ruff!")
Husky.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Husky.setDefense(3, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
