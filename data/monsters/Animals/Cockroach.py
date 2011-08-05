import game.monster

cockroach = game.monster.genMonster("cockroach", (284, 8593), "a cockroach")
cockroach.setTargetChance(0)
cockroach.bloodType("venom")
cockroach.setHealth(1)
cockroach.setExperience(0)
cockroach.setSpeed(200) #incorrect
cockroach.walkAround(1,1,1) # energy, fire, poison
cockroach.setBehavior(summonable=200, attackable=1, hostile=0, illusionable=200, convinceable=200, pushable=1, pushItems=0, pushCreatures=0, targetDistance=0, runOnHealth=1)
cockroach.setImmunity(0,0,0) # paralyze, invisible, lifedrain
cockroach.setDefense(0, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
