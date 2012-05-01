nightslayer = genMonster("Nightslayer", (152, 6080), "a nightslayer")
nightslayer.setOutfit(95, 95, 95, 95)#?
nightslayer.setHealth(400, healthmax=400)
nightslayer.bloodType(color="blood")
nightslayer.setDefense(armor=27, fire=1, earth=1, energy=1, ice=1.1, holy=1, death=1, physical=1, drown=1)#
nightslayer.setExperience(250)
nightslayer.setSpeed(250)#
nightslayer.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
nightslayer.walkAround(energy=0, fire=0, poison=0)
nightslayer.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
nightslayer.regMelee(70)#
nightslayer.loot( ("midnight shard", 17.75) )