import game.monster

minotaur = game.monster.genMonster("Minotaur", (25, 5969), "a minotaur")
minotaur.setHealth(100)
minotaur.bloodType(color="blood")
minotaur.setDefense(armor=11, fire=0.8, earth=1, energy=1, ice=1.1, holy=0.9, death=1.1, physical=1, drown=1)
minotaur.setExperience(50)
minotaur.setSpeed(170)
minotaur.setBehavior(summonable=330, attackable=1, hostile=1, illusionable=1, convinceable=330, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=0)
minotaur.walkAround(energy=1, fire=1, poison=1)
minotaur.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
minotaur.voices("Kaplar!")