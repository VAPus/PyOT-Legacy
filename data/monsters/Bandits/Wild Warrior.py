<-- Wild_Warrior -->
Wild_Warrior = game.monster.genMonster("Wild Warrior", (131, 6090), "a Wild Warrior")
Wild_warrior.setOutfit(57, 57, 57, 57)
Wild_Warrior.setTargetChance(10)
Wild_Warrior.bloodType("blood")
Wild_Warrior.setHealth(135)
Wild_Warrior.setExperience(60)
Wild_Warrior.setSpeed(190) # Correct
Wild_Warrior.walkAround(1,1,1) # energy, fire, poison
Wild_Warrior.setBehavior(summonable=420, hostile=1, illusionable=420, convinceable=420, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=13)
Wild_Warrior.voices("Gimme your money!", "An enemy!")
Wild_Warrior.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Wild_Warrior.setDefense(11, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.1, drown=1.0)