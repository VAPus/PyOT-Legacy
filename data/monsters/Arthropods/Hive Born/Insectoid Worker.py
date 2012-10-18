Insectoid_Worker = game.monster.genMonster("Insectoid Worker", (403, 5980), "a insectoid worker")
Insectoid_Worker.setHealth(950)
Insectoid_Worker.bloodType(color="slime")
Insectoid_Worker.setDefense(armor=15, fire=1.1, earth=0, energy=1.05, ice=1.05, holy=1, death=1, physical=0.95, drown=1)
Insectoid_Worker.setExperience(650)
Insectoid_Worker.setSpeed(300) #unknown
Insectoid_Worker.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Insectoid_Worker.walkAround(energy=1, fire=1, poison=0)
Insectoid_Worker.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=1)
Insectoid_Worker.regMelee(110) #poisons you for up to 8 hp/turn