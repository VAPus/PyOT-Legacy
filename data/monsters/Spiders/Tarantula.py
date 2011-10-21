
tarantula = game.monster.genMonster("Tarantula", (219, 5995), "a tarantula")
tarantula.setHealth(225)
tarantula.bloodType(color="slime")
tarantula.setDefense(armor=20, fire=1.15, earth=0, energy=0.9, ice=1.1, holy=1, death=1, physical=1, drown=1)
tarantula.setExperience(120)
tarantula.setSpeed(280)
tarantula.setBehavior(summonable=485, hostile=1, illusionable=1, convinceable=485, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
tarantula.walkAround(energy=1, fire=1, poison=0)
tarantula.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
tarantula.regMelee(90) #Poisons you for 1-2 hp/turn
tarantula.loot( (2148, 100, 40), ("tarantula egg", 10.0), ("brass legs", 3.25), ("steel helmet", 1.0), ("plate shield", 2.0), ("time ring", 0.0025) )