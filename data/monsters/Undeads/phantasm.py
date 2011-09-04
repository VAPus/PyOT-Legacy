import game.monster

phantasm = game.monster.genMonster("Phantasm", (241, 6344), "a phantasm")
phantasm.setHealth(3950)
phantasm.bloodType(color="undead")
phantasm.setDefense(armor=25, fire=1.1, earth=0.8, energy=1.1, ice=0.8, holy=1.1, death=0, physical=0, drown=1)
phantasm.setExperience(4400)
phantasm.setSpeed(280)
phantasm.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=400)
phantasm.walkAround(energy=1, fire=1, poison=1)
phantasm.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
phantasm.voices("Oh my, you forgot to put your pants on!", "Weeheeheeheehee!", "Its nothing but a dream.", "Dream a little dream with me!", "Give in.")
phantasm.regMelee(470)