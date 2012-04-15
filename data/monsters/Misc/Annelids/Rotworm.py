Rotworm = game.monster.genMonster(_("Rotworm"), (26, 5967), _("a Rotworm"))
Rotworm.setTargetChance(0)
Rotworm.bloodType("blood")
Rotworm.setHealth(65)
Rotworm.setExperience(40)
Rotworm.setSpeed(116)
Rotworm.walkAround(1,1,1) # energy, fire, poison
Rotworm.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=305, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Rotworm.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Rotworm.setDefense(9, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Rotworm.regMelee(40)
Rotworm.loot( ("lump of dirt", 10.0), ("meat", 20.0, 2), (2148, 100, 17), ("ham", 19.75, 2), (3976, 5.75, 3), ("sword", 3.0), ("mace", 4.25) )