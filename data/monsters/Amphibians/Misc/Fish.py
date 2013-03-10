fish = genMonster("Fish", (455, 2667), "a fish")
fish.setHealth(25)
fish.bloodType("blood")
fish.setDefense(armor=5, fire=0, earth=0, energy=1, ice=1, holy=1, death=1, physical=1, drown=0)
fish.setExperience(0)
fish.setSpeed(250) #?
fish.setBehavior(summonable=0, hostile=0, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=25) #runs hostile?
fish.walkAround(energy=1, fire=0, poison=0)
fish.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
fish.voices("Blib!", "Blub!")