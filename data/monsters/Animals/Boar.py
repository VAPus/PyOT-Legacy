# bad
boar = game.monster.genMonster("boar", (380, 13239), "a boar")
boar.bloodType("blood")
boar.setHealth(198)
boar.setExperience(60)
boar.setTargetChance(10)
boar.setSpeed(200) #incorrect
boar.walkAround(1,1,1) # energy, fire, poison
boar.setBehavior(summonable=465, hostile=1, illusionable=1, convinceable=465, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=20)
boar.voices("Grunt Grunt, Grunt")
boar.setImmunity(0,0,0) # paralyze, invisible, lifedrain
boar.setDefense(3, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
boar.loot( ('haunch of boar', 31.5, 2), (2148, 100, 20) ),
boar.regMelee(50)#or more