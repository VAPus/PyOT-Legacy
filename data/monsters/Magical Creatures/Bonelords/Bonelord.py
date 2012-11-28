Bonelord = genMonster("Bonelord", (17, 5992), "a Bonelord")
Bonelord.setTargetChance(10)
Bonelord.bloodType("blood")
Bonelord.setHealth(260)
Bonelord.setExperience(170)
Bonelord.setSpeed(150) # correct
Bonelord.walkAround(1,1,0) # energy, fire, poison
Bonelord.setBehavior(summonable=0, hostile=1, illusionable=1, convinceable=0, pushable=0, pushItems=1, pushCreatures=0, targetDistance=4, runOnHealth=0)
Bonelord.voices("You've got the look!", "Let me take a look at you.", "Eye for eye!", "I've got to look!", "Here's looking at you!")
Bonelord.setImmunity(0,1,1) # paralyze, invisible, lifedrain
Bonelord.setDefense(5, fire=1.1, earth=1.0, energy=1.0, ice=0.8, holy=1.0, death=1.0, physical=1.0, drown=1.0)
Bonelord.summon("Skeleton", 10)
Bonelord.maxSummons(2)
Bonelord.regMelee(5)
Bonelord.loot( ("morning star", 6.75), ("longsword", 8.5), (3031, 100, 48), ("two handed sword", 4.0), ("spellbook", 4.75), ("steel shield", 3.5), ("small flask of eyedrops", 5.5), ("terra rod", 0.5), ("bonelord eye", 1.0), ("mana potion", 0.25), ("bonelord shield", 0.0025) )