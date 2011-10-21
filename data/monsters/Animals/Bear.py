bear = game.monster.genMonster("Bear", (16, 5974), "a bear")
bear.bloodType("blood")
bear.setHealth(80)
bear.setExperience(23)
bear.setTargetChance(10)
bear.setSpeed(156) # speed correct
bear.walkAround(1,1,1) # energy, fire, poison
bear.setBehavior(summonable=300, hostile=1, illusionable=1, convinceable=300, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=15)
bear.voices("Grrrr", "Groar")
bear.setImmunity(0,0,0) # paralyze, invisible, lifedrain
bear.setDefense(7, fire=1.0, earth=1.0, energy=1.0, ice=1.1, holy=0.9, death=1.5, physical=1.0, drown=1.0)
bear.loot( ('meat', 38.75), ('ham', 19.5), ('bear paw', 1.75, 3), ('honeycomb', 0.75) )
bear.regMelee(25)