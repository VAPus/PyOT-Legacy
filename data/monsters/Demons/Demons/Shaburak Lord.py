shaburak_lord = genMonster("Shaburak Lord", (409, 5980), "a shaburak lord")#corpse
shaburak_lord.setHealth(2100, healthmax=2100)
shaburak_lord.bloodType("blood")
shaburak_lord.setDefense(armor=30, fire=1, earth=1.3, energy=0.5, ice=0.5, holy=1, death=1, physical=1, drown=1)#
shaburak_lord.setExperience(1200)
shaburak_lord.setSpeed(300)#
shaburak_lord.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
shaburak_lord.walkAround(energy=0, fire=0, poison=0)
shaburak_lord.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
shaburak_lord.voices("GREEN IS MEAN!", "WE RULE!", "POWER TO THE SHABURAK!", "DEATH TO THE ASKARAK!", "ONLY WE ARE TRUE DEMONS!")
shaburak_lord.regMelee(200)#
shaburak_lord.loot( ("brown mushroom", 6.25), (2148, 100, 162), ("strong health potion", 8.25), ("platinum coin", 59.75, 2), ("steel boots", 0.5), ("small ruby", 16.75, 5), ("strong mana potion", 6.25), ("energy ring", 1.0), ("magma coat", 0.5), ("magic sulphur", 1.5), ("wand of inferno", 0.5) )