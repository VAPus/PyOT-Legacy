import game.monster

Monk = game.monster.genMonster("Monk", (57, 6080), "a Monk")
Monk.setTargetChance(10)
Monk.bloodType("blood")
Monk.setHealth(240)
Monk.setExperience(200)
Monk.setSpeed(240) # Correct
Monk.walkAround(1,1,1) # energy, fire, poison
Monk.setBehavior(summonable=600, hostile=1, illusionable=600, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
Monk.voices("Repent Heretic!", "A prayer to the almighty one!", "I will punish the sinners!")
Monk.setImmunity(0,1,0) # paralyze, invisible, lifedrain
Monk.setDefense(27, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=0.5, death=0.5, physical=1.05, drown=1.0)