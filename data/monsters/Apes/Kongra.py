<-- Kongra -->
Kongra = game.monster.genMonster("Kongra", (116, 6043), "a Kongra")
Kongra.setTargetChance(10)
Kongra.bloodType("blood")
Kongra.setHealth(340)
Kongra.setExperience(115)
Kongra.setSpeed(184) # Correct
Kongra.walkAround(1,1,1) # energy, fire, poison
Kongra.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=10)
Kongra.voices("Ungh! Ungh!", "Hugah!", "Huaauaauaauaa!")
Kongra.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Kongra.setDefense(20, fire=0.8, earth=0.9, energy=0.95, ice=1.15, holy=1.0, death=1.05, physical=1.0, drown=1.0)