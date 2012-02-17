#still somewhat unknown
furious_orc_berserker = game.monster.genMonster("Durious Orc Berserker", (35, 5995), "a furious orc berserker")
furious_orc_berserker.setHealth(2, healthmax=2)
furious_orc_berserker.bloodType(color="blood")
furious_orc_berserker.setDefense(-1)
furious_orc_berserker.setExperience(0)
furious_orc_berserker.setSpeed(200)
furious_orc_berserker.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
furious_orc_berserker.walkAround(energy=0, fire=0, poison=0)
furious_orc_berserker.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
furious_orc_berserker.regMelee(0) #attacks but doesnt do damage?