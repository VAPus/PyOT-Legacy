
orc_shaman = game.monster.genMonster("Orc Shaman", (6, 5978), "an orc shaman")
orc_shaman.setHealth(115)
orc_shaman.bloodType(color="blood")
orc_shaman.setDefense(armor=10, fire=1, earth=1.1, energy=0.5, ice=1, holy=0.9, death=1.05, physical=1, drown=1)
orc_shaman.setExperience(110)
orc_shaman.setSpeed(180)
orc_shaman.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=4, runOnHealth=0)
orc_shaman.walkAround(energy=1, fire=1, poison=1)
orc_shaman.setImmunity(paralyze=0, invisible=1, lifedrain=0, drunk=1)
orc_shaman.summon("snake", 10)
orc_shaman.maxSummons(4)
orc_shaman.voices("Huumans stinkk!", "Grak brrretz gulu.")
orc_shaman.regMelee(15) #incorrect