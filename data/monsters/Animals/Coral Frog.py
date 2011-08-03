import game.monster
<-- coral frog -->
coral frog = game.monster.genMonster("coral frog", (226, 6079), "a coral frog")
coral_Frog.setOutfit(69, 66, 69, 66)
coral frog.setTargetChance(10)
coral frog.bloodType("blood")
coral frog.setHealth(60)
coral frog.setExperience(20)
coral frog.setSpeed(200) #incorrect
coral frog.walkAround(1,1,1) # energy, fire, poison
coral frog.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
coral frog.voices("Ribbit!", "Ribbit! Ribbit!")
coral frog.setImmunity(0,0,0) # paralyze, invisible, lifedrain
coral frog.setDefense(10, fire=1.1, earth=1.0, energy=1.0, ice=0.85, holy=1.0, death=1.0, physical=1.0, drown=1.0)
