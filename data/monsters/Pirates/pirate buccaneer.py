import game.monster

pirate_buccaneer = game.monster.genMonster("Pirate Buccaneer", (97, 6080), "a pirate buccaneer")
pirate_buccaneer.setHealth(425)
pirate_buccaneer.bloodType(color="blood")
pirate_buccaneer.setDefense(armor=18, fire=1.05, earth=0.9, energy=1.05, ice=1.05, holy=0.9, death=1.05, physical=1.05, drown=1)
pirate_buccaneer.setExperience(250)
pirate_buccaneer.setSpeed(230)
pirate_buccaneer.setBehavior(summonable=0, hostile=2, illusionable=1, convinceable=595, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=20, targetChange=0)
pirate_buccaneer.walkAround(energy=1, fire=1, poison=1)
pirate_buccaneer.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)
pirate_buccaneer.voices("Give up!", "Hiyaa", "Plundeeeeer!")
pirate_buccaneer.regMelee(160)