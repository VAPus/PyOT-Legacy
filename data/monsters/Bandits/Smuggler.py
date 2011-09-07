<-- Smuggler -->
Smuggler = game.monster.genMonster("Smuggler", (134, 6080), "a Smuggler")
Smuggler.setOutfit(95, 0, 113, 115)
Smuggler.setTargetChance(10)
Smuggler.bloodType("blood")
Smuggler.setHealth(130)
Smuggler.setExperience(48)
Smuggler.setSpeed(176) # Correct
Smuggler.walkAround(1,1,1) # energy, fire, poison
Smuggler.setBehavior(summonable=390, hostile=1, illusionable=390, convinceable=390, pushable=0, pushItems=1, pushCreatures=0, targetDistance=1, runOnHealth=13)
Smuggler.voices("You saw something you shouldn't", "I will silence you forever!")
Smuggler.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Smuggler.setDefense(9, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.05, physical=1.05, drown=1.0)