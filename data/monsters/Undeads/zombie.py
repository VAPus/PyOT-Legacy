
zombie = game.monster.genMonster("Zombie", (311, 9875), "a zombie")
zombie.setHealth(500)
zombie.bloodType(color="undead")
zombie.setDefense(armor=15, fire=0.5, earth=0, energy=0, ice=0, holy=1, death=0, physical=1, drown=0)
zombie.setExperience(280)
zombie.setSpeed(180)#incorrect speed?
zombie.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
zombie.walkAround(energy=0, fire=1, poison=0)
zombie.setImmunity(paralyze=1, invisible=0, lifedrain=1, drunk=1)
zombie.voices("Mst.... klll....", "Whrrrr... ssss.... mmm.... grrrrl", "Dnnnt... cmmm... clsrrr....", "Httt.... hmnnsss...")
zombie.regMelee(130)