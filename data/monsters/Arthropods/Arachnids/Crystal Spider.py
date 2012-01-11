
crystal_spider = game.monster.genMonster("Crystal Spider", (263, 7344), "a crystal spider")
crystal_spider.setHealth(1250)
crystal_spider.bloodType(color="undead")
crystal_spider.setDefense(armor=47, fire=1, earth=0.8, energy=1.2, ice=1, holy=0.8, death=1, physical=1, drown=1)
crystal_spider.setExperience(900)
crystal_spider.setSpeed(340)
crystal_spider.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
crystal_spider.walkAround(energy=1, fire=0, poison=0)
crystal_spider.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
crystal_spider.voices("Screeech!")
crystal_spider.regMelee(250) #poisons you for up to 8hp/turn
crystal_spider.loot( ("shard", 0.75), ("steel helmet", 5.0), ("plate armor", 9.75), ("ice cube", 5.5), ("sniper arrow", 20.5, 6), (2148, 100, 94), ("brass legs", 8.25), ("crystal sword", 0.5), ("time ring", 0.75), (5879, 1.75), ("knight armor", 0.25), ("strong mana potion", 0.5), ("knight legs", 0.25), ("sapphire hammer", 0.0025), ("platinum amulet", 0.25), ("glacier mask", 0.25), ("jewelled backpack", 0.0025) )