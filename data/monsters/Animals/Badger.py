import game.monster

Badger = game.monster.genMonster("Badger", (105, 6034), "a badger")
Badger.bloodType("blood")
Badger.setHealth(23)
Badger.setExperience(5)
Badger.setTargetChance(10)
Badger.setSpeed(200) # speed incorrect
Badger.walkAround(1,1,1) # energy, fire, poison
Badger.setBehavior(summonable=200, attackable=1, hostile=1, illusionable=1, convinceable=200, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=5)
Badger.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Badger.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Badger.loot( ('beetroot', 32.5), ('badger fur', 8.5), ('acorn', 4.5) )
