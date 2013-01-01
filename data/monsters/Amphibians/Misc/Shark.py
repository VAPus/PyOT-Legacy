shark = genMonster("Shark", (8, 5980), "a shark")
shark.setHealth(1200, healthmax=1200)
shark.bloodType("blood")
shark.setDefense(armor=15, fire=1, earth=0.8, energy=1.05, ice=1, holy=1, death=1, physical=1, drown=0)
shark.setExperience(700)
shark.setSpeed(300) #incorrect
shark.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
shark.walkAround(energy=1, fire=0, poison=0)
shark.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
shark.voices("Rarr chomp chomp!")
shark.regMelee(10) #?