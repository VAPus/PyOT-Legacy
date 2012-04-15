Carrion_Worm = game.monster.genMonster(_("Carrion Worm"), (192, 6069), _("a Carrion Worm"))
Carrion_Worm.setTargetChance(0)
Carrion_Worm.bloodType("blood")
Carrion_Worm.setHealth(145)
Carrion_Worm.setExperience(70)
Carrion_Worm.setSpeed(130) # Correct
Carrion_Worm.walkAround(1,1,1) # energy, fire, poison
Carrion_Worm.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=380, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Carrion_Worm.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Carrion_Worm.setDefense(9, fire=1.05, earth=0.8, energy=0.9, ice=1.05, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Carrion_Worm.regMelee(45)
Carrion_Worm.loot( ("meat", 14.0, 2), (2148, 100, 26), ("carrion worm fang", 11.0), (3976, 8.25, 2) )