swarmer = genMonster("swarmer", (460, 15385), "a swarmer")
swarmer.setHealth(460, healthmax=460)
swarmer.bloodType("slime")
swarmer.setDefense(armor=25, fire=1.1, earth=0, energy=0.25, ice=1.05, holy=1, death=1, physical=1, drown=1)
swarmer.setExperience(350)
swarmer.setSpeed(250) #incorrect
swarmer.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=50)
swarmer.walkAround(energy=1, fire=1, poison=0)
swarmer.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
swarmer.regMelee(100) #poison you for up to 4 hp/turn