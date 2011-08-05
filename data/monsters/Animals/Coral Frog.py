import game.monster

corall_frog = game.monster.genMonster("Corall Frog", (226, 6079), "a corall_frog")
corall_frog.setOutfit(69, 66, 69, 66)
corall_frog.setTargetChance(10)
corall_frog.bloodType("blood")
corall_frog.setHealth(60)
corall_frog.setExperience(20)
corall_frog.setSpeed(200) #incorrect
corall_frog.walkAround(1,1,1) # energy, fire, poison
corall_frog.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
corall_frog.voices("Ribbit!", "Ribbit! Ribbit!")
corall_frog.setImmunity(0,0,0) # paralyze, invisible, lifedrain
corall_frog.setDefense(10, fire=1.1, earth=1.0, energy=1.0, ice=0.85, holy=1.0, death=1.0, physical=1.0, drown=1.0)
