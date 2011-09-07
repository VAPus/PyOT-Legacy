import game.monster

minotaur_archer = game.monster.genMonster("Minotaur Archer", (24, 5982), "a minotaur archer")
minotaur_archer.setHealth(100)
minotaur_archer.bloodType(color="blood")
minotaur_archer.setDefense(armor=7, fire=0.8, earth=1, energy=1, ice=1.1, holy=0.9, death=1.05, physical=1, drown=1)
minotaur_archer.setExperience(65)
minotaur_archer.setSpeed(170)
minotaur_archer.setBehavior(summonable=390, hostile=1, illusionable=1, convinceable=390, pushable=1, pushItems=0, pushCreatures=1, targetDistance=4, runOnHealth=10)
minotaur_archer.walkAround(energy=0, fire=0, poison=0)
minotaur_archer.setImmunity(paralyze=0, invisible=0, lifedrain=0, drunk=0)
minotaur_archer.voices("Ruan Wihmpy!", "Kaplar!")