import game.monster

Terror_Bird = game.monster.genMonster("Terror Bird", (218, 6057), "a Terror Bird")
Terror_Bird.setTargetChance(10)
Terror_Bird.bloodType("blood")
Terror_Bird.setHealth(300)
Terror_Bird.setExperience(150)
Terror_Bird.setSpeed(212)
Terror_Bird.walkAround(1,1,1) # energy, fire, poison
Terror_Bird.setBehavior(summonable=490, attackable=1, hostile=1, illusionable=490, convinceable=490, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Terror_Bird.voices("Carrah! Carrah!", "Gruuuh Gruuuh.", "CRAAAHHH!")
Terror_Bird.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Terror_Bird.setDefense(15, fire=1.1, earth=1.1, energy=0.8, ice=0.8, holy=1.0, death=1.05, physical=1.0, drown=1.0)
