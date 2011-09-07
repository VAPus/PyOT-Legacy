<-- Hero -->
Hero = game.monster.genMonster("Hero", (73, 6080), "a Hero")
Hero.setTargetChance(10)
Hero.bloodType("blood")
Hero.setHealth(1400)
Hero.setExperience(1200)
Hero.setSpeed(280) # Correct
Hero.walkAround(0,1,0) # energy, fire, poison
Hero.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=0, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
Hero.voices("Let's have a fight!", "I will sing a tune at your grave.", "Have you seen princess Lumelia?", "Welcome to my battleground!")
Hero.setImmunity(1,1,1) # paralyze, invisible, lifedrain
Hero.setDefense(39, fire=0.7, earth=0.5, energy=0.6, ice=0.9, holy=0.5, death=1.2, physical=0.9, drown=1.0)