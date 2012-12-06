Crawler = genMonster("Crawler", (456, 15292), "a crawler")
Crawler.setHealth(0, healthmax=None)
Crawler.bloodType("slime")
Crawler.setDefense(armor=30, fire=1.1, earth=0, energy=1, ice=1.05, holy=1.05, death=1, physical=1, drown=1)
Crawler.setExperience(1000)
Crawler.setSpeed(250) #incorrect
Crawler.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=40)
Crawler.walkAround(energy=1, fire=1, poison=0)
Crawler.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
Crawler.regMelee(120) #can poison you for up to 4 hp/turn