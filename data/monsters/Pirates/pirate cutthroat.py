import game.monster

pirate_cutthroat = game.monster.genMonster("pirate_cutthroat", (96, 6080), "a pirate_cutthroat")
pirate_cutthroat.setHealth(325)
pirate_cutthroat.bloodType(color="blood")
pirate_cutthroat.setDefense(armor=0, fire=1.05, earth=0.9, energy=1, ice=0.95, holy=0.8, death=1.05, physical=1, drown=1)
pirate_cutthroat.setExperience(175)
pirate_cutthroat.setSpeed(230)
pirate_cutthroat.setBehavior(summonable=0, attackable=1, hostile=2, illusionable=1, convinceable=495, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=20, targetChange=0))
pirate_cutthroat.walkAround(energy=1, fire=1, poison=1)
pirate_cutthroat.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)
pirate_cutthroat.voices("Give up!", "Plundeeeeer!", "Hiyaa!")
pirate_cutthroat.regMelee(175)#+poison