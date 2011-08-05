import game.monster

Dog = game.monster.genMonster("Dog", (32, 5971), "a Dog")
Dog.setTargetChance(10)
Dog.bloodType("blood")
Dog.setHealth(20)
Dog.setExperience(0)
Dog.setSpeed(124) # correct
Dog.walkAround(1,1,1) # energy, fire, poison
Dog.setBehavior(summonable=220, attackable=1, hostile=1, illusionable=220, convinceable=220, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=8)
Dog.voices("Wuff Wuff")
Dog.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Dog.setDefense(3, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
