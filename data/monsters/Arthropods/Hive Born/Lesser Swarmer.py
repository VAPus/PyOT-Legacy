lesser_swarmer = game.monster.genMonster("Lesser Swarmer", (460, 15385), "a lesser swarmer")
lesser_swarmer.setHealth(230, healthmax=230)
lesser_swarmer.bloodType(color="slime")
lesser_swarmer.setDefense(armor=25, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
lesser_swarmer.setExperience(0)
lesser_swarmer.setSpeed(250) #incorrect
lesser_swarmer.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
lesser_swarmer.walkAround(energy=1, fire=1, poison=0) #?
lesser_swarmer.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)
lesser_swarmer.regMelee(75) #poisons you for up to 3 hp/turn