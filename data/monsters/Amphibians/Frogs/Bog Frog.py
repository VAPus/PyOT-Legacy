bogl_frog = genMonster("Bog Frog", (226, 6079), "a bog frog") #corpse?
bogl_frog.setOutfit(255, 255, 255, 255) #color
bogl_frog.setTargetChance(10)
bogl_frog.type("blood")
bogl_frog.health(25)
bogl_frog.experience(0)
bogl_frog.speed(200) #incorrect
bogl_frog.walkAround(1,1,1) #?
bogl_frog.behavior(summonable=0, hostile=0, illusionable=1, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=25) #pushable?
bogl_frog.voices("Ribbit!", "Ribbit! Ribbit!")
bogl_frog.immunity(0,0,0) # paralyze, invisible, lifedrain