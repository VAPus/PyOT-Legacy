import game.monster
<-- cat -->
cat = game.monster.genMonster("cat", (276, 7637), "a cat")
cat.bloodType("blood")
cat.setHealth(20)
cat.setExperience(0)
cat.setTargetChance(10)
cat.setSpeed(124) #?
cat.walkAround(1,1,1) # energy, fire, poison
cat.setBehavior(summonable=220, attackable=1, hostile=1, illusionable=220, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
cat.voices("Mew!", "Meow!", "Meow meow!")
cat.setImmunity(0,0,0) # paralyze, invisible, lifedrain
cat.setDefense(3, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
