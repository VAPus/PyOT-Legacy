import game.monster

crocodile = game.monster.genMonster("Crocodile", (119, 6046), "a crocodile")
crocodile.setHealth(105)
crocodile.bloodType(color="blood")
crocodile.setDefense(armor=10, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
crocodile.setExperience(40)
crocodile.setSpeed(240)
crocodile.setBehavior(summonable=350, attackable=1, hostile=1, illusionable=1, convinceable=350, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=10)
crocodile.walkAround(energy=1, fire=1, poison=1)
crocodile.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)