
swamp_troll = game.monster.genMonster("Swamp Troll", (76, 6018), "a swamp troll")
swamp_troll.setHealth(55)
swamp_troll.bloodType(color="slime")
swamp_troll.setDefense(armor=8, fire=1.05, earth=0.85, energy=1, ice=1, holy=1, death=1, physical=1, drown=1)
swamp_troll.setExperience(65)
swamp_troll.setSpeed(128)
swamp_troll.setBehavior(summonable=320, hostile=1, illusionable=1, convinceable=320, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=15)
swamp_troll.walkAround(energy=1, fire=1, poison=1)
swamp_troll.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
swamp_troll.voices("Me strong! Me ate spinach!", "Groar!", "Grrrr")
swamp_troll.regMelee(13)#+1hp/turn poison
swamp_troll.loot( ("leather boots", 10.0), (2148, 100, 5), ("fish", 59.5), ("torch", 14.5), ("swamp grass", 3.0), ("spear", 12.75), ("troll green", 1.0), ("fishing rod", 0.0025) )