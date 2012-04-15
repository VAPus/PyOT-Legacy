Seagull = game.monster.genMonster(_("Seagull"), (223, 6076), _("a seagull"))
Seagull.setTargetChance(0)
Seagull.bloodType("blood")
Seagull.setHealth(25)
Seagull.setExperience(0)
Seagull.setSpeed(200) #incorrect
Seagull.walkAround(1,1,1) # energy, fire, poison
Seagull.setBehavior(summonable=250, hostile=0, illusionable=1, convinceable=250, pushable=1, pushItems=0, pushCreatures=0, targetDistance=0, runOnHealth=25)
Seagull.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Seagull.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Seagull.regMelee(3)#summons only? probably incorrect information