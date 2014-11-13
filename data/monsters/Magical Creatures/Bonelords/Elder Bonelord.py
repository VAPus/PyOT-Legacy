Elder_Bonelord = genMonster("Elder Bonelord", (226, 6037), "a Elder Bonelord")
Elder_Bonelord.setTargetChance(10)
Elder_Bonelord.type("blood")
Elder_Bonelord.health(500)
Elder_Bonelord.experience(280)
Elder_Bonelord.speed(170) # correct
Elder_Bonelord.walkAround(1,1,0) # energy, fire, poison
Elder_Bonelord.behavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=4, runOnHealth=0)
Elder_Bonelord.voices("Inferior creatures, bow before my power!", "Let me take a look at you!", "659978", "54764!", "653768764!")
Elder_Bonelord.immunity(0,1,1) # paralyze, invisible, lifedrain
Elder_Bonelord.defense(13, fire=1.1, earth=0, energy=0.8, ice=0.7, holy=1.0, death=0.7, physical=1.0, drown=1.0)
Elder_Bonelord.summon("Gazer", 10)
Elder_Bonelord.summon("Crypt Shambler", 10)
Elder_Bonelord.maxSummons(6)
Elder_Bonelord.regMelee(50)
Elder_Bonelord.loot( ("sniper arrow", 22.5, 4), ("strong mana potion", 0.75), ("elder bonelord tentacle", 20.75), (2148, 100, 87), ("steel shield", 2.25), ("small flask of eyedrops", 10.0), ("two handed sword", 2.5), ("giant eye", 0.5), ("spellbook", 1.25) )