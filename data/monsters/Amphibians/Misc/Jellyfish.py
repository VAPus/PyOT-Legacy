jellyfish = game.monster.genMonster("Jellyfish", (452, 15284), "a jellyfish")
jellyfish.setHealth(55)
jellyfish.bloodType(color="blood")
jellyfish.setDefense(armor=5, fire=0, earth=0, energy=1.05, ice=1, holy=1, death=1, physical=1.05, drown=0)
jellyfish.setExperience(0)
jellyfish.setSpeed(250) #?
jellyfish.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
jellyfish.walkAround(energy=1, fire=0, poison=0)
jellyfish.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
jellyfish.voices("Luuurrrp!")
jellyfish.regMelee(5) #?