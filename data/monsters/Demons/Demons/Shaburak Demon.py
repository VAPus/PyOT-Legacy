shaburak_demon = game.monster.genMonster("Shaburak Demon", (417, 5980), "a shaburak demon")#corpse
shaburak_demon.setHealth(1500)
shaburak_demon.bloodType(color="blood")
shaburak_demon.setDefense(armor=26, fire=1, earth=1.3, energy=0.5, ice=0.5, holy=1, death=1, physical=1, drown=1)#
shaburak_demon.setExperience(900)
shaburak_demon.setSpeed(300)#
shaburak_demon.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
shaburak_demon.walkAround(energy=0, fire=0, poison=0)
shaburak_demon.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
shaburak_demon.voices("GREEN IS MEAN!", "WE RULE!", "POWER TO THE SHABURAK!", "DEATH TO THE ASKARAK!", "ONLY WE ARE TRUE DEMONS!")
shaburak_demon.regMelee(140)
shaburak_demon.loot( (2148, 100, 252), ("wand of inferno", 0.5), ("small ruby", 15.0, 5), ("strong mana potion", 5.25), ("royal spear", 37.0, 6), ("energy ring", 1.25), ("strong health potion", 6.25), ("piggy bank", 1.0), ("brown mushroom", 3.25), ("bullseye potion", 0.25), ("magma legs", 0.0025), ("magic sulphur", 0.0025) )