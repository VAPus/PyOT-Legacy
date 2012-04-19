destroyer = game.monster.genMonster("Destroyer", (236, 6320), "a Destroyer")
destroyer.setHealth(3700, healthmax=3700)
destroyer.bloodType(color="blood")
destroyer.setDefense(armor=37, fire=0.7, earth=0.8, energy=0, ice=1.15, holy=1.03, death=0.8, physical=0.8, drown=1)
destroyer.setExperience(2500)
destroyer.setSpeed(380)
destroyer.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
destroyer.walkAround(energy=0, fire=1, poison=1)
destroyer.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
destroyer.voices("COME HERE AND DIE!", "Destructiooooon!", "It's a good day to destroy!")
destroyer.regMelee(500)
destroyer.loot( (2148, 100, 341), ("metal spike", 6.75), ("meat", 55.0), ("demonic essence", 19.0, 3), ("small amethyst", 11.25, 2), ("crowbar", 15.0), ("plate armor", 5.0), ("pick", 6.0), ("mind stone", 0.75), ("dark armor", 10.0), ("steel boots", 1.0), ("burst arrow", 71.25, 12), ("soul orb", 6.75), ("platinum coin", 8.0, 3), ("great health potion", 1.0), ("dreaded cleaver", 0.75), ("skull helmet", 0.0025), ("crystal necklace", 0.5), ("chaos mace", 1.0), ("giant sword", 1.5), ("death ring", 0.0025) )