<-- Nomad -->
Nomad = game.monster.genMonster("Nomad", (146, 6080), "a Nomad")
Nomad.setOutfit(114, 20, 22, 2)
Nomad.setAddons(3)
Nomad.setTargetChance(10)
Nomad.bloodType("blood")
Nomad.setHealth(160)
Nomad.setExperience(60)
Nomad.setSpeed(190) # Correct
Nomad.walkAround(1,1,1) # energy, fire, poison
Nomad.setBehavior(summonable=420, attackable=1, hostile=1, illusionable=0, convinceable=420, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=25)
Nomad.voices("I will leave your remains to the vultures!", "We are the true sons of the desert!", "We are swift as the wind of the desert!", "Your riches will be mine!")
Nomad.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Nomad.setDefense(7, fire=0.8, earth=1.0, energy=1.0, ice=1.1, holy=0.8, death=1.1, physical=1.1, drown=1.0)