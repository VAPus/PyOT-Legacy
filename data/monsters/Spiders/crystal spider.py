import game.monster

crystal_spider = game.monster.genMonster("Crystal Spider", (263, 7344), "a crystal spider")
crystal_spider.setHealth(1250)
crystal_spider.bloodType(color="undead")
crystal_spider.setDefense(armor=25, fire=1, earth=0.8, energy=1.2, ice=1, holy=0.8, death=1, physical=1, drown=1)
crystal_spider.setExperience(900)
crystal_spider.setSpeed(340)
crystal_spider.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
crystal_spider.walkAround(energy=1, fire=0, poison=0)
crystal_spider.setImmunity(paralyze=1, invisible=1, lifedrain=0, drunk=0)
crystal_spider.voices("Screeech!")