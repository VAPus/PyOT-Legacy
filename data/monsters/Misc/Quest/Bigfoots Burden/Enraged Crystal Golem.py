enraged_crystal_golem = game.monster.genMonster("Enraged Crystal Golem", (508, 18466), "an enraged crystal golem")  #mostly unkniown including blood
enraged_crystal_golem.setHealth(700, healthmax=700)
enraged_crystal_golem.bloodType(color="blood")
enraged_crystal_golem.setDefense(armor=30, fire=0, earth=1, energy=1, ice=0, holy=1, death=1, physical=0.85, drown=1)
enraged_crystal_golem.setExperience(550)
enraged_crystal_golem.setSpeed(350) #unknown
enraged_crystal_golem.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
enraged_crystal_golem.walkAround(energy=0, fire=0, poison=0)
enraged_crystal_golem.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
enraged_crystal_golem.voices("Crrrrk! Chhhhr!")
enraged_crystal_golem.regMelee(150)