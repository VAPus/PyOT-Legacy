
giant_spider = game.monster.genMonster("Giant Spider", (38, 5977), "a giant spider")
giant_spider.setHealth(1300)
giant_spider.bloodType(color="slime")
giant_spider.setDefense(armor=50, fire=1.1, earth=0, energy=0.8, ice=0.8, holy=1, death=1, physical=1, drown=1)
giant_spider.setExperience(900)
giant_spider.setSpeed(280)
giant_spider.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
giant_spider.walkAround(energy=0, fire=1, poison=0)
giant_spider.setImmunity(paralyze=0, invisible=0, lifedrain=1, drunk=1)
giant_spider.summon("poison spider", 10)
giant_spider.maxSummons(2)
giant_spider.regMelee(300) #poisons you for 5-8 hp/turn
giant_spider.loot( (2148, 100, 98), ("poison arrow", 79.5, 12), ("steel helmet", 5.25), ("plate armor", 10.25), ("time ring", 0.75), ("brass legs", 8.5), (5879, 2.25), ("strong health potion", 1.0), ("knight legs", 0.25), ("knight armor", 0.25), ("platinum amulet", 0.25), ("lightning headband", 0.0025) )