#mostly unknown
doomsday_cultist = game.monster.genMonster("Doomsday Cultist", (194, 6080), "a doomsday cultist")
doomsday_cultist.setOutfit(95, 95, 95, 95) #need correct colors
doomsday_cultist.setHealth(125)
doomsday_cultist.bloodType(color="blood")
doomsday_cultist.setDefense(armor=5, fire=1, earth=0.8, energy=0.7, ice=0.9, holy=1.2, death=0, physical=1, drown=1)
doomsday_cultist.setExperience(100)
doomsday_cultist.setSpeed(250)
doomsday_cultist.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
doomsday_cultist.walkAround(energy=0, fire=0, poison=0)
doomsday_cultist.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
doomsday_cultist.regMelee(100)
doomsday_cultist.loot( ("midnight shard", 4.0) )