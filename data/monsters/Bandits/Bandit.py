<-- Bandit -->
Bandit = game.monster.genMonster("Bandit", (129, 6080), "a Bandit")
Bandit.setOutfit(58, 59, 45, 114)
Bandit.setTargetChance(10)
Bandit.bloodType("blood")
Bandit.setHealth(245)
Bandit.setExperience(65)
Bandit.setSpeed(180) # Correct
Bandit.walkAround(1,1,1) # energy, fire, poison
Bandit.setBehavior(summonable=450, attackable=1, hostile=1, illusionable=450, convinceable=450, pushable=1, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=25)
Bandit.voices("Hand me your purse!", "Your money or your life!")
Bandit.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Bandit.setDefense(10, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.1, drown=1.0)