
mutated_human = game.monster.genMonster("Mutated Human", (323, 9107), "a mutated human")
mutated_human.setHealth(240)
mutated_human.bloodType(color="blood")
mutated_human.setDefense(armor=27, fire=1, earth=0, energy=1, ice=0.8, holy=1.25, death=0, physical=1, drown=1)
mutated_human.setExperience(150)
mutated_human.setSpeed(240)
mutated_human.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=1, targetDistance=1, runOnHealth=0)
mutated_human.walkAround(energy=1, fire=1, poison=0)
mutated_human.setImmunity(paralyze=1, invisible=1, lifedrain=1, drunk=1)
mutated_human.voices("Take that creature off my back!! I can feel it!", "You will regret interrupting my studies!", "You will be the next infected one... CRAAAHHH!", "Science... is a curse.", "Run as fast as you can.", "Oh by the gods! What is this... aaaaaargh!")
mutated_human.regMelee(90) #poisons you 3 hp/turn
mutated_human.loot( (2148, 100, 130), ("fishbone", 10.5), ("cheese", 8.25), ("sword", 4.75), ("mutated flesh", 19.75), ("scale armor", 7.5), ("fern", 0.5), (3976, 11.0, 2), ("rusty armor", 1.75), ("strange talisman", 5.0), ("peanut", 0.5), ("silver amulet", 0.0025) )