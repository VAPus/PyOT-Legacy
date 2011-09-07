import game.monster

spit_nettle = game.monster.genMonster("Spit Nettle", (221, 6062), "a spit nettle")
spit_nettle.setHealth(150, healthmax=150)
spit_nettle.bloodType(color="slime")
spit_nettle.setDefense(armor=13, fire=1.1, earth=0, energy=0, ice=0.8, holy=1, death=1, physical=1, drown=1)
spit_nettle.setExperience(25)
spit_nettle.setSpeed(0)
spit_nettle.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
spit_nettle.walkAround(energy=0, fire=0, poison=0)
spit_nettle.setImmunity(paralyze=1, invisible=0, lifedrain=0, drunk=1)