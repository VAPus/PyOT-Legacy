<-- Assassin -->
Assassin = game.monster.genMonster("Assassin", (152, 6080), "a Assassin")
Assassin.setOutfit(95, 95, 95, 95)
Assassin.setAddons(3)
Assassin.setTargetChance(10)
Assassin.bloodType("blood")
Assassin.setHealth(175)
Assassin.setExperience(105)
Assassin.setSpeed(224) # correct
Assassin.walkAround(1,1,1) # energy, fire, poison
Assassin.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=1, convinceable=450, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=0)
Assassin.voices("You are on my deathlist!", "Die!", "Feel the hand of death!")
Assassin.setImmunity(0,1,0) # paralyze, invisible, lifedrain
Assassin.setDefense(22, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.25, drown=1.0)