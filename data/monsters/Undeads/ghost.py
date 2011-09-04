import game.monster

ghost = game.monster.genMonster("Ghost", (48, 5993), "a ghost")
ghost.setHealth(150)
ghost.bloodType(color="undead")
ghost.setDefense(armor=10, fire=1, earth=0, energy=1, ice=1, holy=1, death=0, physical=0, drown=0)
ghost.setExperience(120)
ghost.setSpeed(160)
ghost.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
ghost.walkAround(energy=1, fire=1, poison=0)
ghost.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=0)
ghost.voices("Huh!", "Shhhhhh", "Buuuuuh")
ghost.regMelee(80)