import game.monster

witch = game.monster.genMonster("Witch", (54, 6081), "a witch")
witch.setHealth(300)
witch.bloodType(color="blood")
witch.setDefense(armor=10, fire=1, earth=0.8, energy=0, ice=1, holy=1, death=1.05, physical=1.05, drown=1)
witch.setExperience(120)
witch.setSpeed(180)
witch.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=4, runOnHealth=30)
witch.walkAround(energy=0, fire=1, poison=1)
witch.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
witch.voices("Herba budinia ex!", "Horax Pokti!", "Hihihihi!")