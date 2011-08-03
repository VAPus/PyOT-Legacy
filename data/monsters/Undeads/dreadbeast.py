import game.monster

dreadbeast = game.monster.genMonster("Dreadbeast", (101, 6030), "a dreadbeast")
dreadbeast.setHealth(795)
dreadbeast.bloodType(color="undead")
dreadbeast.setDefense(35, armor=20, fire=0.45, earth=0, energy=0.85, ice=0.65, holy=1.5, death=0, physical=0.7, drown=0.25)
dreadbeast.setExperience(250)
dreadbeast.setSpeed(210)
dreadbeast.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=800, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
dreadbeast.walkAround(energy=0, fire=0, poison=0)
dreadbeast.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=0)