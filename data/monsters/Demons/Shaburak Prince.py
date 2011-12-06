shaburak_prince = game.monster.genMonster("Shaburak Prince", (418, 5980), "a shaburak prince")#corpse
shaburak_prince.setHealth(2600, healthmax=2600)
shaburak_prince.bloodType(color="blood")
shaburak_prince.setDefense(armor=33, fire=1, earth=1.3, energy=0.5, ice=0.5, holy=1, death=1, physical=1, drown=1)#
shaburak_prince.setExperience(1700)
shaburak_prince.setSpeed(300)#
shaburak_prince.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
shaburak_prince.walkAround(energy=0, fire=0, poison=0)
shaburak_prince.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
shaburak_prince.voices("GREEN IS MEAN!", "WE RULE!", "POWER TO THE SHABURAK!", "DEATH TO THE ASKARAK!", "ONLY WE ARE TRUE DEMONS!")
shaburak_prince.regMelee(320)