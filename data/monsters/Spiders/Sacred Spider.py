#most values are unknown
Sacred_Spider = game.monster.genMonster("Sacred Spider", (219, 5995), "a sacred spider")
Sacred_Spider.setHealth(550)
Sacred_Spider.bloodType(color="slime")
Sacred_Spider.setDefense(armor=20, fire=1.05, earth=0, energy=0.9, ice=1.1, holy=1, death=1, physical=1, drown=1)
Sacred_Spider.setExperience(330)
Sacred_Spider.setSpeed(280)
Sacred_Spider.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
Sacred_Spider.walkAround(energy=1, fire=1, poison=0)
Sacred_Spider.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
Sacred_Spider.regMelee(150) #Poisons you (up to 4 hp per turn) ##max melee damage could be wrong