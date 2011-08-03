import game.monster
<-- crystal_wolf --> # Bad fixed
crystal_wolf = game.monster.genMonster("crystal wolf", (226, 6079), "a crystal wolf") # unkown yet
crystal_wolf.setTargetChance(10)
crystal_wolf.bloodType("blood")
crystal_wolf.setHealth(750)
crystal_wolf.setExperience(275)
crystal_wolf.setSpeed(200) #incorrect
crystal_wolf.walkAround(1,1,1) # energy, fire, poison
crystal_wolf.setBehavior(summonable=0, attackable=1, hostile=1, illusionable=0, convinceable=305, pushable=0, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
crystal_wolf.voices("Raaaarrr!")
crystal_wolf.setImmunity(0,0,0) # paralyze, invisible, lifedrain
crystal_wolf.setDefense(30, fire=1.1, earth=1.0, energy=1.0, ice=0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
