Wild_Warrior = game.monster.genMonster("Wild Warrior", (131, 6090), "a Wild Warrior")
Wild_Warrior.setOutfit(57, 57, 57, 57)
Wild_Warrior.setTargetChance(10)
Wild_Warrior.bloodType("blood")
Wild_Warrior.setHealth(135)
Wild_Warrior.setExperience(60)
Wild_Warrior.setSpeed(190) # Correct
Wild_Warrior.walkAround(1,1,1) # energy, fire, poison
Wild_Warrior.setBehavior(summonable=420, hostile=1, illusionable=1, convinceable=420, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=13)
Wild_Warrior.voices("Gimme your money!", "An enemy!")
Wild_Warrior.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Wild_Warrior.setDefense(11, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.1, drown=1.0)
Wild_Warrior.regMelee(70)
Wild_Warrior.loot( ('brass shield', 18.0), (2148, 100, 30), ('mace', 10.0), ('leather legs', 8.25), ('chain helmet', 5.0), ('steel shield', 1.0), ('axe', 29.75), ('egg', 15.25, 2), ('iron helmet', 0.75), ('brass armor', 2.5), ('doll', 0.5) )