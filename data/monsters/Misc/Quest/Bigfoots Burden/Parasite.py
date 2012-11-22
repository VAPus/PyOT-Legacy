Parasite = genMonster("Parasite", (82, 6023), "a parasite")
Parasite.setHealth(550, healthmax=550)
Parasite.bloodType("slime")
Parasite.setDefense(armor=10, fire=1.1, earth=0, energy=0.9, ice=1.05, holy=1, death=1, physical=1, drown=1)
Parasite.setExperience(0)
Parasite.setSpeed(135)
Parasite.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Parasite.walkAround(energy=1, fire=1, poison=0)
Parasite.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
Parasite.regMelee(35)#poison 1p/turn