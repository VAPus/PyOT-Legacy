import game.monster

Elder_Bonelord = game.monster.genMonster("Elder Bonelord", (226, 6079), "a Elder Bonelord")
Elder_Bonelord.setTargetChance(10)
Elder_Bonelord.bloodType("blood")
Elder_Bonelord.setHealth(500)
Elder_Bonelord.setExperience(280)
Elder_Bonelord.setSpeed(170) # correct
Elder_Bonelord.walkAround(1,1,0) # energy, fire, poison
Elder_Bonelord.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=4, runOnHealth=0)
Elder_Bonelord.voices("Inferior creatures, bow before my power!", "Let me take a look at you!", "659978", "54764!", "653768764!")
Elder_Bonelord.setImmunity(0,1,1) # paralyze, invisible, lifedrain
Elder_Bonelord.setDefense(13, fire=1.1, earth=0, energy=0.8, ice=0.7, holy=1.0, death=0.7, physical=1.0, drown=1.0)