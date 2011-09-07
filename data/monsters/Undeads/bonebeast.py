import game.monster

bonebeast = game.monster.genMonster("Bonebeast", (101, 6030), "a bonebeast")
bonebeast.setHealth(515)
bonebeast.bloodType(color="undead")
bonebeast.setDefense(armor=20, fire=1.1, earth=0, energy=1, ice=1, holy=1.25, death=0, physical=1, drown=0)
bonebeast.setExperience(580)
bonebeast.setSpeed(210)
bonebeast.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
bonebeast.walkAround(energy=1, fire=1, poison=0)
bonebeast.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
bonebeast.voices("Knooorrrrr!", "Cccchhhhhhhhh!")
bonebeast.regMelee(200)#+poison up to 5/hp turn