Gladiator = genMonster("Gladiator", (131, 6080), "a Gladiator")
Gladiator.setOutfit(78, 3, 79, 114)
Gladiator.setTargetChance(10)
Gladiator.bloodType("blood")
Gladiator.setHealth(185)
Gladiator.setExperience(90)
Gladiator.setSpeed(200)
Gladiator.walkAround(1,1,1) # energy, fire, poison
Gladiator.setBehavior(summonable=0, hostile=1, illusionable=0, convinceable=470, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=18)
Gladiator.voices("You are no match for me!", "Feel my prowess.", "Take this!")
Gladiator.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Gladiator.setDefense(15, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=0.9, death=1.05, physical=0.95, drown=1.0)
Gladiator.regMelee(90)
Gladiator.loot( ("plate shield", 9.25), ("mace", 10.75), ("chain helmet", 4.75), (3031, 100, 28), ("sword", 10.75), ("meat", 20.5), ("brass armor", 1.75), ("steel shield", 0.75), ("iron helmet", 0.25), ("belted cape", 0.5) )