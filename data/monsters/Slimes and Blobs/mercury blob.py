import game.monster

mercury_blob = game.monster.genMonster("Mercury Blob", (316, 9961), "a mercury blob")
mercury_blob.setHealth(150)
mercury_blob.bloodType(color="undead")
mercury_blob.setDefense(armor=10, fire=0.9, earth=0.35, energy=1, ice=0.85, holy=0.35, death=0, physical=0.9, drown=1)
mercury_blob.setExperience(180)
mercury_blob.setSpeed(210)
mercury_blob.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
mercury_blob.walkAround(energy=1, fire=1, poison=1)
mercury_blob.setImmunity(paralyze=0, invisible=0, lifedrain=1, drunk=1)
mercury_blob.voices("Crackle")