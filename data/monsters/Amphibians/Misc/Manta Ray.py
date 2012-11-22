manta_ray = genMonster("Manta Ray", (449, 15276), "a manta ray")
manta_ray.setHealth(680)
manta_ray.bloodType("blood")
manta_ray.setDefense(armor=15, fire=0, earth=0, energy=1.05, ice=1, holy=1, death=1, physical=1, drown=0)
manta_ray.setExperience(125)
manta_ray.setSpeed(250) #?
manta_ray.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
manta_ray.walkAround(energy=0, fire=0, poison=0)
manta_ray.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
manta_ray.voices("Flap flap flap!")
manta_ray.regMelee(110) #poison you for up to 6 hp/turn