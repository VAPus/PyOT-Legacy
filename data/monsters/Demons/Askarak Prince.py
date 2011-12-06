askarak_prince = game.monster.genMonster("askarak Prince", (419, 5980), "a askarak prince")#corpse
askarak_prince.setHealth(2600, healthmax=2600)
askarak_prince.bloodType(color="blood")
askarak_prince.setDefense(armor=33, fire=1.3, earth=0, energy=0.5, ice=0.5, holy=1, death=1, physical=1, drown=1)#
askarak_prince.setExperience(1700)
askarak_prince.setSpeed(300)#
askarak_prince.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
askarak_prince.walkAround(energy=0, fire=0, poison=0)
askarak_prince.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
askarak_prince.voices("DEATH TO THE SHABURAK!", "ONLY WE ARE TRUE DEMONS!", "GREEN WILL RULE!", "RED IS MAD")
askarak_prince.regMelee(260)#