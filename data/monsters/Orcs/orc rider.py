import game.monster

orc_rider = game.monster.genMonster("Orc Rider", (4, 6010), "an orc rider")
orc_rider.setHealth(180)
orc_rider.bloodType(color="blood")
orc_rider.setDefense(armor=11, fire=1, earth=1.1, energy=0.8, ice=1, holy=0.9, death=1.1, physical=1, drown=1)
orc_rider.setExperience(110)
orc_rider.setSpeed(340)
orc_rider.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=490, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
orc_rider.walkAround(energy=0, fire=0, poison=0)
orc_rider.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=1)
orc_rider.voices("Orc arga Huummmak!", "Grrrrrrr")
orc_rider.regMelee(130)