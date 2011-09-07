import game.monster

mutated_human = game.monster.genMonster("Mutated Human", (323, 9107), "a mutated human")
mutated_human.setHealth(240)
mutated_human.bloodType(color="blood")
mutated_human.setDefense(armor=25, fire=1, earth=0, energy=1, ice=0.8, holy=1.25, death=0, physical=1, drown=1)
mutated_human.setExperience(150)
mutated_human.setSpeed(240)
mutated_human.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
mutated_human.walkAround(energy=1, fire=1, poison=0)
mutated_human.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
mutated_human.voices("Take that creature off my back!! I can feel it!", "You will regret interrupting my studies!", "You will be the next infected one... CRAAAHHH!", "Science... is a curse.", "Run as fast as you can.", "Oh by the gods! What is this... aaaaaargh!")