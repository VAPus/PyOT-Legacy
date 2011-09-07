import game.monster

orc_berserker = game.monster.genMonster("Orc Berserker", (8, 5980), "an orc berserker")
orc_berserker.setHealth(210)
orc_berserker.bloodType(color="blood")
orc_berserker.setDefense(armor=12, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
orc_berserker.setExperience(195)
orc_berserker.setSpeed(250)
orc_berserker.setBehavior(summonable=590, hostile=1, illusionable=1, convinceable=590, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
orc_berserker.walkAround(energy=1, fire=1, poison=1)
orc_berserker.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=1)
orc_berserker.voices("KRAK ORRRRRRK!")