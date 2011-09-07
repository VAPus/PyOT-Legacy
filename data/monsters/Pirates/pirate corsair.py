import game.monster

pirate_corsair = game.monster.genMonster("pirate_corsair", (98, 6080), "a pirate_corsair")
pirate_corsair.setHealth(675)
pirate_corsair.bloodType(color="blood")
pirate_corsair.setDefense(armor=20, fire=1.1, earth=0.8, energy=1, ice=0.95, holy=0.9, death=1.05, physical=1, drown=1)
pirate_corsair.setExperience(350)
pirate_corsair.setSpeed(230)
pirate_corsair.setBehavior(summonable=0, hostile=2, illusionable=1, convinceable=775, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0, targetChange=0)
pirate_corsair.walkAround(energy=1, fire=1, poison=1)
pirate_corsair.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)
pirate_corsair.voices("Hiyaa!", "Give up!", "Plundeeeeer!")
pirate_corsair.regMelee(170)