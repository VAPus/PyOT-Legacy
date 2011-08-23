import game.monster

warlock = game.monster.genMonster("Warlock", (130, 6080), "a warlock")
warlock.setOutfit(19, 71, 128, 128) #needs an addon
warlock.setHealth(3500)
warlock.bloodType(color="blood")
warlock.setDefense(armor=20, fire=0, earth=0.05, energy=0, ice=0, holy=1.08, death=1, physical=1.05, drown=1)
warlock.setExperience(4000)
warlock.setSpeed(220)
warlock.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=800)
warlock.walkAround(energy=0, fire=0, poison=0)
warlock.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
warlock.voices("Even a rat is a better mage than you!", "Learn the secret of our magic! YOUR death!", "We don't like intruders!")