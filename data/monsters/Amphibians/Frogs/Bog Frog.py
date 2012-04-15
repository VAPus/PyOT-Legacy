bogl_frog = game.monster.genMonster(_("Bog Frog"), (226, 6079), _("a bog frog")) ##corpse?
bogl_frog.setOutfit(255, 255, 255, 255) ##color
bogl_frog.setTargetChance(10)
bogl_frog.bloodType("blood")
bogl_frog.setHealth(25)
bogl_frog.setExperience(0)
bogl_frog.setSpeed(200) #incorrect
bogl_frog.walkAround(1,1,1) ##?
bogl_frog.setBehavior(summonable=0, hostile=0, illusionable=1, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=25) ##pushable?
bogl_frog.voices("Ribbit!", "Ribbit! Ribbit!")
bogl_frog.setImmunity(0,0,0) # paralyze, invisible, lifedrain