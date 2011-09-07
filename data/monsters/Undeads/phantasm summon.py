import game.monster

phantasm_summon = game.monster.genMonster("Phantasm", (241, 6344), "a phantasm")
phantasm_summon.setHealth(65)
phantasm_summon.bloodType(color="undead")
phantasm_summon.setDefense(armor=25, fire=1.1, earth=0.8, energy=1.1, ice=0.8, holy=1.1, death=0, physical=0, drown=1)
phantasm_summon.setExperience(0)
phantasm_summon.setSpeed(280)
phantasm_summon.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
phantasm_summon.walkAround(energy=1, fire=1, poison=1)
phantasm_summon.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
phantasm_summon.voices("Oh my, you forgot to put your pants on!", "Weeheeheeheehee!", "Its nothing but a dream.", "Dream a little dream with me!", "Give in.")
phantasm_summon.regMelee(200)#wrong