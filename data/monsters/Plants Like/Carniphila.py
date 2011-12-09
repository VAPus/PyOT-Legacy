
carniphila = game.monster.genMonster("Carniphila", (120, 6047), "a carniphila")
carniphila.setHealth(255)
carniphila.bloodType(color="slime")
carniphila.setDefense(armor=29, fire=1.2, earth=0, energy=0.9, ice=0.8, holy=1, death=1, physical=1, drown=1)
carniphila.setExperience(150)
carniphila.setSpeed(240)
carniphila.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
carniphila.walkAround(energy=1, fire=1, poison=0)
carniphila.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
carniphila.regMelee(100) #poisons you 5 hp/turn
carniphila.loot( ("seeds", 0.5), ("dark mushroom", 8.0), ("shadow herb", 1.0), (2148, 100, 40), ("carniphila seeds", 4.0), ("corncob", 1.25), ("sling herb", 0.75, 2), ("carrot on a stick", 0.0025) )