Assassin = game.monster.genMonster("Assassin", (152, 6080), "a Assassin")
Assassin.setOutfit(95, 95, 95, 95)
Assassin.setAddons(3)
Assassin.setTargetChance(10)
Assassin.bloodType("blood")
Assassin.setHealth(175)
Assassin.setExperience(105)
Assassin.setSpeed(224) # correct
Assassin.walkAround(1,1,1) # energy, fire, poison
Assassin.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=450, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
Assassin.voices("You are on my deathlist!", "Die!", "Feel the hand of death!")
Assassin.setImmunity(0,1,0) # paralyze, invisible, lifedrain
Assassin.setDefense(22, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.25, drown=1.0)
Assassin.regMelee(120)
Assassin.loot( ('throwing star', 50.25, 14), (2148, 100, 50), ('knife', 10.25), ('torch', 42.5, 2), ('viper star', 18.25, 7), ('combat knife', 3.75), ('steel shield', 1.0), ('steel helmet', 2.75), ('plate shield', 2.0), ('battle shield', 1.5), ('leopard armor', 0.5), ('horseman helmet', 0.25), ('small diamond', 0.0025) )