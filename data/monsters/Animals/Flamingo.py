import game.monster

Flamingo = game.monster.genMonster("Flamingo", (212, 6054), "a flamingo")
Flamingo.setTargetChance(10)
Flamingo.bloodType("blood")
Flamingo.setHealth(25)
Flamingo.setExperience(0)
Flamingo.setSpeed(160) # correct
Flamingo.walkAround(1,1,1) # energy, fire, poison
Flamingo.setBehavior(summonable=250, hostile=0, illusionable=1, convinceable=250, pushable=1, pushItems=0, pushCreatures=0, targetDistance=0, runOnHealth=0)
Flamingo.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Flamingo.setDefense(2, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Flamingo.loot( ('downy feather', 1) )