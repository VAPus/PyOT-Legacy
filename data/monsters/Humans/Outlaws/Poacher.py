Poacher = game.monster.genMonster("Poacher", (129, 6080), "a Poacher")
Poacher.setOutfit(115, 119, 119, 115)
Poacher.setAddons(1)
Poacher.setTargetChance(10)
Poacher.bloodType("blood")
Poacher.setHealth(90)
Poacher.setExperience(70)
Poacher.setSpeed(198) # Correct
Poacher.walkAround(1,1,1) # energy, fire, poison
Poacher.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=530, pushable=1, pushItems=0, pushCreatures=0, targetDistance=1, runOnHealth=9)
Poacher.voices("You will not live to tell anyone!", "You are my game today!", "Look what has stepped into my trap!")
Poacher.setImmunity(0,0,0) # paralyze, invisible, lifedrain
Poacher.setDefense(11, fire=1.0, earth=1.0, energy=1.0, ice=1.0, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Poacher.regMelee(35)
Poacher.loot( ("bow", 14.75), ("leather legs", 25.75), ("leather helmet", 30.0), ("arrow", 100, 17), ("poison arrow", 4.0, 3), ("roll", 12.25, 2), ("torch", 3.5), ("closed trap", 1.0) )