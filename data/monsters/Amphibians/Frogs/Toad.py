Toad = game.monster.genMonster(_("Toad"), (222, 6077), _("a toad"))
Toad.setTargetChance(10)
Toad.bloodType("blood")
Toad.setHealth(135)
Toad.setExperience(60)
Toad.setSpeed(210) #correct
Toad.walkAround(1,1,1) # energy, fire, poison
Toad.setBehavior(summonable=400, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=10)
Toad.voices("Ribbit!", "Ribbit! Ribbit!")
Toad.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Toad.setDefense(7, fire=1.1, earth=0.8, energy=1.0, ice=0.8, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Toad.loot( (2148, 100, 20), ("poisonous slime", 4.25), ("fish", 20.0), ("war hammer", 0.25), ("mace", 3.0) )


Toad.regMelee(30, condition=Condition(CONDITION_POISON, 0, 1, damage=1), conditionChance=100)
Toad.regSelfSpell("Haste", 360, 360, length=5, check=chance(21)) #?
Toad.regTargetSpell(2292, 8, 17, check=chance(21)) #is the range 1?