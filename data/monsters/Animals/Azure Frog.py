import game.monster
Azure_Frog = game.monster.genMonster("Azure Frog", (226, 6079), "an Azure Frog")
Azure_Frog.setOutfit(69, 66, 69, 66)
Azure_Frog.bloodType("blood")
Azure_Frog.setHealth(60)
Azure_Frog.setExperience(20)
Azure_Frog.setTargetChance(10)
Azure_Frog.setSpeed(200) # speed incorrect
Azure_Frog.walkAround(1,1,1) # energy, fire, poison
Azure_Frog.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=305, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Azure_Frog.voices("Ribbit!", "Ribbit! Ribbit!")
Azure_Frog.setImmunity(0,0,0) # paralyze, invisible, lifedrain
azure_Frog.setDefense(10, fire=1.1, earth=1, energy=1, ice=0.85, holy=1.0, death=1.0, physical=1.0, drown=1.0)
