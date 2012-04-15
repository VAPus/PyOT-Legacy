Terror_Bird = game.monster.genMonster("Terror Bird", (218, 6057), "a terror bird")
Terror_Bird.setTargetChance(10)
Terror_Bird.bloodType("blood")
Terror_Bird.setHealth(300)
Terror_Bird.setExperience(150)
Terror_Bird.setSpeed(212)
Terror_Bird.walkAround(1,1,1) # energy, fire, poison
Terror_Bird.setBehavior(summonable=490, hostile=1, illusionable=1, convinceable=490, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Terror_Bird.voices("Carrah! Carrah!", "Gruuuh Gruuuh.", "CRAAAHHH!")
Terror_Bird.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Terror_Bird.setDefense(18, fire=1.1, earth=1.1, energy=0.8, ice=0.8, holy=1.0, death=1.05, physical=1.0, drown=1.0)
Terror_Bird.loot( (2148, 100, 30), ("meat", 48.75, 3), ("terrorbird beak", 11.5), ("colourful feather", 3.0), (3976, 9.0), ("health potion", 1.25), ("seeds", 0.25) )
Terror_Bird.regMelee(90)