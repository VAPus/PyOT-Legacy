dragonling = game.monster.genMonster("Dragonling", (505, 5980), "a dragonling") #mostly unknown including corpse
dragonling.setHealth(2600, healthmax=2600)
dragonling.bloodType(color="blood")
dragonling.setDefense(armor=20, fire=0, earth=1.02, energy=0.98, ice=0.98, holy=1, death=1, physical=1.02, drown=1)
dragonling.setExperience(2200)
dragonling.setSpeed(300) #unknown
dragonling.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
dragonling.walkAround(energy=1, fire=0, poison=0)
dragonling.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
dragonling.voices("FI?", "FCHHHHHHHHHHHHHHHH")
dragonling.regMelee(200)