swarmer_hatchling = game.monster.genMonster("Swarmer Hatchling", (460, 15385), "a swarmer hatchling")
swarmer_hatchling.setHealth(5, healthmax=5)
swarmer_hatchling.bloodType(color="slime")
swarmer_hatchling.setDefense(armor=25, fire=1, earth=1, energy=1, ice=1, holy=1, death=1, physical=1, drown=4)
swarmer_hatchling.setExperience(0)
swarmer_hatchling.setSpeed(250) #incorrect
swarmer_hatchling.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
swarmer_hatchling.walkAround(energy=0, fire=1, poison=0) #?
swarmer_hatchling.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)
name.voices("Flzlzlzlzlzlzlz?")
swarmer_hatchling.regMelee(0)