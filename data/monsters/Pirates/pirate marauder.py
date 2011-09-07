import game.monster

pirate_marauder = game.monster.genMonster("Pirate Marauder ", (93, 6080), "a pirate marauder ")
pirate_marauder.setHealth(210)
pirate_marauder.bloodType(color="blood")
pirate_marauder.setDefense(armor=10, fire=1.1, earth=0.9, energy=1.03, ice=1, holy=0.8, death=1.05, physical=1, drown=1)
pirate_marauder.setExperience(125)
pirate_marauder.setSpeed(230)
pirate_marauder.setBehavior(summonable=0, hostile=2, illusionable=1, convinceable=490, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=20, targetChange=0)
pirate_marauder.walkAround(energy=1, fire=1, poison=1)
pirate_marauder.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)
pirate_marauder.voices("Plundeeeeer!", "Hiyaa!", "Give up!")
pirate_marauder.regMelee(140)