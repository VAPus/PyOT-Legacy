
wailing_widow = game.monster.genMonster("Wailing Widow", (347, 11310), "a wailing widow")
wailing_widow.setHealth(850)
wailing_widow.bloodType(color="slime")
wailing_widow.setDefense(armor=35, fire=1.1, earth=0, energy=1, ice=1, holy=0.9, death=0, physical=1, drown=1)
wailing_widow.setExperience(450)
wailing_widow.setSpeed(280)
wailing_widow.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=366)#does it run?
wailing_widow.walkAround(energy=1, fire=1, poison=0)
wailing_widow.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
wailing_widow.regMelee(120) #poisons you
wailing_widow.loot( (2148, 100, 139), ("health potion", 4.25), ("mana potion", 2.0), (11328, 6.0), ("plate shield", 3.0), ("green mushroom", 1.25), ("zaoan halberd", 1.25), (11329, 0.5) )